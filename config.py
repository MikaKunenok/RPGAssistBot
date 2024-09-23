"""
    This file describes main features of your bot.
    Adjust variables for your person usage
     TOKEN - telegram token of your bot
     TIMEZONE - the one used by the bot
     DEVELOPER - main administrator of the bot (telegram login)

     RULES_URL - where the user can read about the rules, that are implemented by the bot.
                Do not change if you do not change the bot behavior

     INITIAL_DISEASES_DIR - local directory, where json for your default diseases are placed.
                            The simplest one goes with git, so the bot should work "from the box"

     MASTER_PASS - set password, that your masters will use for self register in the bot

     MASTERS - dict of initial masters. It can be changed with bot itself
     PLAYERS - dict of initial players. It can be changed by the bot itself
     the keys in both dicts are telegram users ids.
     Use @RawDataBot at Telegram app to find out your or anybody ids
     **_COMMANDS - lists of commands, that the bot provides for every group of players.
                   Adjust help message for each command as you like.
                   Do not change commands sets and names, until you're not changing the bot code itself.

"""
from infected_player import InfectedPlayer
import disease_reader

TOKEN = "7294933311:AAGrI19fouxT0ZEydyQ5do-W8vnEJoty28A"

# telegram login of the person, who supposed to answer most users questions
DEVELOPER = 'kunenok_mika'
TIMEZONE = "Asia/Tbilisi"
TIMEZONE_COMMON_NAME = "Tbilisi"

#
RULES_URL = "https://docs.google.com/document/d/1V78lwOSnsDeoXex329XXh7I379fNMcIvODqNJy-rUyo"

# telegram login of the person, who supposed to answer most users questions
INITIAL_DISEASES_DIR = "data/default/"
DISEASES = {}

def reset_diseases():
    DISEASES.clear()
    for disease in disease_reader.from_dir(INITIAL_DISEASES_DIR):
        DISEASES[disease.name] = disease


reset_diseases()

MASTER_PASS = 'OrlovSharit'

MASTERS = {
    303236745 : 'Colt',
    154101515 : 'Mika'
}

PLAYERS = {
    154101515  : InfectedPlayer('Mika', is_healer=False),
    303236745  : InfectedPlayer('Colt', is_healer=False),
    5007397746 : InfectedPlayer('Сat', is_healer=True)
}

DEFAULT_COMMANDS = {
    'list_masters' : 'See masters\' usernames'
}

MASTER_COMMANDS = {
    'add_master'   : 'add another master. chat id required',
    'del_master'   : 'delete another master. chat id required',
    'set_masters'  : 'set the list of masters',

    'list_players' : 'show the list of current players and their diseases',
    'add_player'   : 'add new player. chat id and name required',
    'set_sick'     : 'make the player sick. chat id and disease name required',
    'set_rnd_sick' : 'make the player sick with random disease. chat id required',
    'set_healthy'  : 'make the player healthy',

    'set_healer'   : 'make the player a healer. chat id required',
    'del_healer'   : 'remove healer abilities from the player. chat id required',

    'stop_notify'  : 'stop notifications from the bot for the player. chat id required',

    'add_diseases'  : 'add diseases from json file, keep old ones',
    'set_diseases'  : 'set diseases from json file, delete old ones',
    'reset_diseases': 'reset diseases to default'
}
MASTER_COMMANDS.update(DEFAULT_COMMANDS)

PLAYER_COMMANDS = {
    'sick'    : 'set random disease to myself',
    'symptom' : 'get my current symptom',
    'treat'   : 'intake a potion',
    'stop'    : 'stop all notifications from the bot. diseases info is kept'
}
PLAYER_COMMANDS.update(DEFAULT_COMMANDS)

HEALER_COMMANDS = PLAYER_COMMANDS
HEALER_COMMANDS.update({'test': 'test the player. chat id required'})
