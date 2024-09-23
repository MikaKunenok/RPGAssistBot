Welcome to RPG Assist Bot project!

Assist Bot is created for offline RPG masters.
If you're feeling like a machine at the game - that is making simple notes,
 looking at the watch, keeping in mind to notify players about repeated or regular things -
just make this bot to do stupid work.

Let yourself solve exciting tasks, concentrate on the scenario and roleplay!

WHAT IS IT?
Right now this bot fully implements mechanics of Diseases, created by Michail Orlov.
See the rules here
https://docs.google.com/document/d/1V78lwOSnsDeoXex329XXh7I379fNMcIvODqNJy-rUyo
The bot let the master and players fulfil Disease mechanics without interacting in person.
It also notifies each player with his disease progress automatically.

WHO CAN I TALK TO?
If you need to adjust this bot for your needs - feel free to contact me via email or social media
malika.bakhtiarova@gmail.com kunenok_mika

HOW TO START?
config.py - if you just need to launch the bot, go here and change TOKEN, PLAYERS and MASTERS
main.py - launch this file to start your bot

master_commands, player_commands, healer_commands - implements commands for each group of users of your bot

player.py disease.py and infected_player.py - implements the whole mechanics, but do nothing with Telegram

disease_reader.py - implements reading diseases from json files. See "data" directory for json examples

player_notifier.py - implements notifying player on their disease progress in Telegram
