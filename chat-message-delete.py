# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 18:29:03 2020

@author: Richard
"""

import json

import os
import sys

from dow2_replay_module import get_files, remove_chat_messages
from print_functions import print_messages, print_players, print_stats

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











