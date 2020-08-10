# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 18:29:03 2020

@author: Richard
"""

# http://dow2replay.pbworks.com/w/page/18160568/File%20Format
# https://github.com/jpb06/relic-chunky-parser
import json

import os
import sys
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


def get_player_names(data):
    all_player_starts = list(find_all(data, b"FOLDGPLY"))
    
    p1 = data[all_player_starts[0]:all_player_starts[1]]
    p2 = data[all_player_starts[1]:all_player_starts[2]]
    p3 = data[all_player_starts[2]:all_player_starts[3]]
    p4 = data[all_player_starts[3]:all_player_starts[4]]
    p5 = data[all_player_starts[4]:all_player_starts[5]]
    p6 = data[all_player_starts[5]:all_player_starts[6]]
    p7 = data[all_player_starts[6]:all_player_starts[7]]
    p8 = data[all_player_starts[7]:]
    
    players_raw = [get_player_name(p) for p in [p1,p2,p3,p4,p5,p6,p7,p8]]
    
    return players_raw


def get_all_message_locations(data, identifier):
    # first element is from the header part (all players)
    all_mentions = list(find_all(data, identifier))[1:]

    messages = []

    for mention_index in all_mentions:
        whole_message_len = unpack("l", data[mention_index - 16:mention_index-12])[0]
        message_start = mention_index - 20
        message_end = message_start + whole_message_len + 8
        messages.append([message_start, message_end])
        
    return messages


def remove_chat_messages(fname):
    message_data = {"players": None, "message_bodies": []}
    gamedata_fixed = None    
    
    with open(fname, 'rb') as f:
        data = f.read()
    
    players = get_player_names(data)
    
    # store player information as raw (utf-16 encoded) bytearray
    message_data["players"] = players
    
    # remove empty player names (unused slots)
    players = [p for p in players if len(p)]
    
    message_locs = []
    
    for p in players:
        message_locs.extend(get_all_message_locations(data, p))
    
    ml = sorted(message_locs, reverse=True)
    gamedata_fixed = list(data)
    
    for m in ml:
        message_data["message_bodies"].append(gamedata_fixed[m[0]:m[1]])
        del gamedata_fixed[m[0]:m[1]]
        
    return message_data, gamedata_fixed


def print_players(message_data):
    print("\n\nPlayers:")
    
    for index, p in enumerate(message_data["players"]):
        if len(p):
            team = 1 if index < 4 else 2
            # TODO: not implemented - need to parse the header file fully
            race = "not imp."
            player = p.decode("utf-16")
            # TODO: no distinction between player and obs
            print("team {0}\t race: {1}\t player: {2}".format(
                    team,
                    race,
                    player
                )
            )
    
def print_messages(message_data):    
    print(f'\n\nmessages: {len(message_data["message_bodies"])}')
    fixed_message_len = 36
    
    for message in message_data["message_bodies"][::-1]:
        # player name len
        player_len = int.from_bytes(message[16:20], byteorder='little') * 2
        player = bytearray(message[20:20+player_len]).decode('utf-16')
        
        message_start = fixed_message_len + player_len
        message = bytearray(message[message_start:]).decode('utf-16')
        print(f'[{player}]: {message}')
        
    
def get_files(folder):
    return glob.glob(os.path.join(folder, '*.rec'))

def print_stats(stats):
    print("\n\nstats:")
    print(f'{stats["all"]-stats["error"]}/{stats["all"]} files processed')

    print(f'{stats["skipped.exist"]+stats["skipped.unchanged"]} skipped')
    print(f'\t{stats["skipped.exist"]} target file already exist')
    print(f'\t{stats["skipped.unchanged"]} had no changes')

#%%
if __name__ == '__main__':
    
    config_path = "config.prod.json"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    # get job config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(e)
        sys.exit(0)
    
    files = get_files(config["folder_in"])
    
    stats = {
        "skipped.exist": 0,
        "skipped.unchanged": 0,
        "all": len(files),
        "error": 0
    }
    
    # f = files[0]
    for f in files:
        fname = os.path.split(f)[1]

        fout = os.path.join(config["folder_out"], fname)
        
        if not config["force"] and os.path.isfile(fout):
            print(f'skipping {f}, already in {config["folder_out"]}')
            stats["skipped.exist"] += 1
            continue
        else:
            print(f"{f} --> {fout}")
           
        try: 
            message_data, gamedata_fixed = remove_chat_messages(f)
            
            if config["print_players"]:
                print_players(message_data)
            
            if config["print_messages"]:
                print_messages(message_data)
            
            if f == fout and len(message_data["message_bodies"]) == 0:
                stats["skipped.unchanged"] += 1
            
            else:
                with open(fout, 'wb') as f:
                    f.write(bytearray(gamedata_fixed))
                    
        except:
            stats["error"] += 1
            

    print_stats(stats)











