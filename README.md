# dow2-elite-chat-remover
removes ingame chat from dow elite replays.

# setup

1. have python 3 installed (e.g. install anaconda)
2. clone/download this repo to a convenient location on your disk
3. copy the config.demo.json to "config.prod.json"
4. replace the input and output directories to your replay folders 

## usage / config options

1. the config.prod.json needs to be valid json file
2. backslashes need to be escpaed with a backslash (so if you want one backslash "\\", write two "\\\\")
3. only tested on windows
4. for making it work it is probably easiest to create a starter batch file (in this directory) with following content and create a shortcut to the batch file at a convenient location.

  PYTHONPATH=\<FULL PATH TO THIS DIRECTORY\>  
  python chat-message-delete.py

  
following config options are available today:

> folder_in: (string), all files from this folder will be evaluated
> folder_out: (string), this is where the files go, after processing

the output filename is the same name as the corresponding input filename. if you choose the same folder for input and output you also need to set the "force" flag, otherwise the replays will not be overwritten.
> force: (boolean) either "true" or "false" (without the quotation marks)
if force is set true it will overwrite existing files in the "folder_out" directory


> print_players: (boolean) either "true" or "false" (without the quotation marks)
> print_messages: (boolean) either "true" or "false" (without the quotation marks)

These two options control output to the console when converting the files.
> print_players --> prints the player names and teams.
It does not distinguish between active players and observers though.

> print_messages --> prints the ingame chat which will have been removed in the out_folder files.
