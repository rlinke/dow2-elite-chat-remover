# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 20:21:22 2020

@author: Richard
"""


def print_players(message_data):
    print("\n\nPlayers:")
    observers = []
    # first print players of the two teams
    for index, p in enumerate(message_data["player_info"]):
        if "player_name" in p and len(p["player_name"]):
            
            team = 1 if index < 4 else 2
            
            if "player_race" in p and len(p["player_race"]):
                print("team {0}\t race: {1}\t player: {2}".format(
                        team,
                        p["player_race"],
                        p["player_name"]
                    )
                )
            else:
                observers.append(p["player_name"])
    
    # print observers
    if len(observers):
        print("\nobservers:")
        print("\n".join(observers))
                
    
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
        
    
def print_stats(stats):
    print("\n\nstats:")
    print(f'{stats["all"]-stats["error"]}/{stats["all"]} files processed')

    print(f'{stats["skipped.exist"]+stats["skipped.unchanged"]} skipped')
    print(f'\t{stats["skipped.exist"]} target file already exist')
    print(f'\t{stats["skipped.unchanged"]} had no changes')

