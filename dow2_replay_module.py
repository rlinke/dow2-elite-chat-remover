# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 18:29:03 2020

@author: Richard
"""

# http://dow2replay.pbworks.com/w/page/18160568/File%20Format
# https://github.com/jpb06/relic-chunky-parser

import os
from struct import unpack
import glob

def get_player_name(data):
    start = data.find(b"FOLDGPLY")
    player_len = unpack("L", data[start+56:start+60])[0]
    start_player_name = start + 60
    player_name = unpack("{0}s".format(player_len*2), data[start_player_name:start_player_name+player_len*2])[0]
    return player_name


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def get_player_info(player_headers):
    result = []
    
    for p in player_headers:
        result.append({
            "player_name_raw": p["player_name_raw"],
            "player_name" : p["player_name_raw"].decode("utf-16"),
            "player_race": p["player_race_raw"].decode("utf-8")
                
        })
            
    return result


def get_all_message_locations(data, identifier, start_index=0):
    # first element is from the header part (all players)
    all_mentions = [i for i in list(find_all(data, identifier)) if i > start_index]

    messages = []

    for mention_index in all_mentions:
        whole_message_len = unpack("l", data[mention_index - 16:mention_index-12])[0]
        message_start = mention_index - 20
        message_end = message_start + whole_message_len + 8
        messages.append([message_start, message_end])
        
    return messages


def remove_chat_messages(fname):
    message_data = {"player_info": None, "message_bodies": []}
    gamedata_fixed = None    
    
    with open(fname, 'rb') as f:
        data = f.read()
        
    # not completely right ... the header_finished index is still not completely correct.
    # but should be better than before
    header_finished, headers = get_header_info(data)

    player_info = get_player_info(headers)
    
    # store player information as raw (utf-16 encoded) bytearray
    message_data["player_info"] = player_info
    
    # remove empty player names (unused slots)
    players = [p for p in player_info if len(p["player_name_raw"])]
    
    message_locs = []
    
    for p in players:
        message_locs.extend(get_all_message_locations(data, p["player_name_raw"], header_finished))
    
    ml = sorted(message_locs, reverse=True)
    gamedata_fixed = list(data)
    
    for m in ml:
        message_data["message_bodies"].append(gamedata_fixed[m[0]:m[1]])
        del gamedata_fixed[m[0]:m[1]]
        
    return message_data, gamedata_fixed


def get_files(folder):
    return glob.glob(os.path.join(folder, '*.rec'))






def get_full_header_len(data, offset):
    # get last 
    start_header = data.find(b"FOLDGPLY", offset)
    
    if start_header == -1:
        return {}
    
    # fixed length player info field:
    fixed_0 = 56 # the offset of the fixed header until the first variable field
    fixed_1 = 8 # 8 --> 8 byte field between var. length fields
    fixed_2 = 16+12+6
    fixed_3 = 4
    fixed_4 = 4 # final header appendix in the end
    
    # | header fixed ... | player len | player string utf-16 | ... | race len | player race (utf-8) | ... | badge | legion
    # variable length fields:
    # 1. player name. starts at start + 56 (including length field)
    # 2. player race. starts at player_offset+player_len + fixed_1
    # 3. data:badges: start at race_offset + race-len + fixed_2
    # 4. legion: (utf-16 *2) offset at badged_offset + badges_len + fixed_3
    dynamic_player_name_len = 0
    dynamic_player_race_len = 0
    dynamic_badges_len = 0
    dynamic_legion_len = 0
    
    # first variable field: player name
    start_player_name_len_field = start_header + fixed_0
    start_player_name = start_player_name_len_field + 4
    dynamic_player_name_len = unpack("L", data[start_player_name_len_field:start_player_name_len_field+4])[0] * 2 
    player_name_raw = unpack("{0}s".format(dynamic_player_name_len), data[start_player_name:start_player_name+dynamic_player_name_len])[0]
    
    # second variable field: player race
    start_player_race_len = start_player_name + fixed_1 + dynamic_player_name_len
    start_race_name = start_player_race_len + 4
    dynamic_player_race_len = unpack("L", data[start_player_race_len:start_player_race_len+4])[0]     
    player_race_raw = unpack("{0}s".format(dynamic_player_race_len), data[start_race_name:start_race_name+dynamic_player_race_len])[0]

    # third variable field: player badges
    start_player_badges_len = start_race_name + fixed_2 + dynamic_player_race_len
    start_badges_name = start_player_badges_len + 4
    dynamic_badges_len = unpack("L", data[start_player_badges_len:start_player_badges_len+4])[0]      
    player_badges_raw = unpack("{0}s".format(dynamic_badges_len), data[start_badges_name:start_badges_name+dynamic_badges_len])[0]

    # fourth variable field: player legion / customizable (unsafe)
    start_legion_len = start_badges_name + fixed_3 + dynamic_badges_len    
    start_legion_name = start_legion_len + 4
    dynamic_legion_len = unpack("L", data[start_legion_len:start_legion_len+4])[0] * 2      
    player_legion_raw = unpack("{0}s".format(dynamic_legion_len), data[start_legion_name:start_legion_name+dynamic_legion_len])[0]

    all_fixed_len = fixed_0 + fixed_1 + fixed_2 + fixed_3 + fixed_4  
    all_dynamic_len = dynamic_player_name_len + dynamic_player_race_len  + dynamic_badges_len + dynamic_legion_len
    full_header_len = all_fixed_len + all_dynamic_len

    return {
        "fixed": all_fixed_len,
        "dynamic": all_dynamic_len,
        "full": full_header_len,
        "player_name_raw": player_name_raw,
        "player_race_raw": player_race_raw,
        "player_badges_raw": player_badges_raw,
        "player_legion_raw": player_legion_raw
        
    }
    
    
def get_header_info(data):
    index = data.find(b"FOLDGPLY")

    headers = []
    for _ in range(8):
        header = get_full_header_len(data, index)        
        index += header['full']
        headers.append(header)
            
    return index, headers
    
"""

    # fixed length?    
    chunk_length = unpack("<L",data[start+12:start+16])[0]
    
    start_player_name

    # get the two variable length fields
    player_len = unpack("L", data[start+56:start+60])[0] * 2        
    start_2 = start_player_name + player_len
    player_race_len = unpack("L", data[start_2+8:start_2+12])[0]

"""
    
    
    
    
    
    
    
    
    
    