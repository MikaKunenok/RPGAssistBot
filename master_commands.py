import time
import random
import json

from the_bot import bot, set_commands
import config
import disease_reader
import utilities
from disease import Disease
from infected_player import InfectedPlayer
from player_notifier import Notifier


def only_master_wrapper(func):
    def wrap(message):
        if message.chat.id in config.MASTERS:
            func(message)
        else:
            bot.send_message(message.chat.id, 'You are not allowed to do this.')

    return wrap


@bot.message_handler(commands=['add_master'])
@only_master_wrapper
def add_master(message):
    bot.send_message(message.chat.id, 'Type new master username.\n' +
                     'WARNING! You cannot add user as master before he\she entered the bot themselves')
    bot.register_next_step_handler(message, do_add_master)


def do_add_master(message):
    try:
        username = utilities.clear(message.text)
        chat_id = config.get_id(username)
        if chat_id in config.PLAYERS:
            del config.PLAYERS[chat_id]
        config.MASTERS.update({chat_id: username})
        set_commands(chat_id, config.MASTER_COMMANDS)
        bot.send_message(message.chat.id, '@%s is a master' % username)
        bot.send_message(chat_id, 'Hello, @%s! You are a master here now!' % username)
    except config.PrivacyError as err:
        bot.send_message(message.chat.id, err)


@bot.message_handler(commands=['del_master'])
@only_master_wrapper
def del_master(message):
    bot.send_message(message.chat.id, 'Type masters usernames as "name1 name2 name3"')
    bot.register_next_step_handler(message, do_del_master)


def do_del_master(message):
    masters = utilities.split_string(message.text)
    for master in masters:
        try:
            chat_id = config.get_id(master)
            if chat_id in config.MASTERS:
                del config.MASTERS[chat_id]
                bot.send_message(message.chat.id, '@%s is not a master any more' % master)
                bot.send_message(chat_id, 'Hello! You was deleted from masters, sorry')
            else:
                bot.send_message(message.chat.id, '@%s was not a master ever' % master)
        except config.PrivacyError as err:
            bot.send_message(message.chat.id, err)


@bot.message_handler(commands=['set_masters'])
@only_master_wrapper
def set_masters_command(message):
    bot.send_message(message.chat.id, 'Type masters usernames as "name1 name2 name3"')
    bot.register_next_step_handler(message, do_set_masters)


def do_set_masters(message):
    masters = utilities.split_string(message.text)
    for master in masters:
        try:
            chat_id = config.get_id(master)
            config.MASTERS.update({chat_id: master})
            set_commands(chat_id, config.MASTER_COMMANDS)
            bot.send_message(message.chat.id, '@%s is known as master' % master)
            bot.send_message(chat_id, 'Hello, @%s! You are now known here as a master!' % master)
        except config.PrivacyError as err:
            bot.send_message(message.chat.id, err)


@bot.message_handler(commands=['list_players'])
@only_master_wrapper
def list_players_command(message):
    for chat_id, player in config.PLAYERS.items():
        try:
            username = config.get_username(chat_id)
            notify = '@%s\nRole Name: %s\nStatus: ' % (username, player.name)
            if player.is_dead():
                notify += 'is dead\n'
            elif player.is_sick():
                notify += 'sick with %s\n' % player.disease.name
            else:
                notify += 'healthy\n'
            if player.is_healer:
                notify += 'Is healer'
            bot.send_message(message.chat.id, notify)
        except config.PrivacyError as err:
            bot.send_message(message.chat.id, err)


@bot.message_handler(commands=['add_player'])
@only_master_wrapper
def add_player(message):
    bot.send_message(message.chat.id, 'Type players username and role name as ' +
                     '"username1 name1; username2 name2; ..."')
    bot.register_next_step_handler(message, do_add_player)


def do_add_player(message):
    players = message.text.split(';')
    for player in players:
        try:
            username, name = utilities.split_string(player, 2)
            chat_id = config.get_id(username)
            if chat_id in config.MASTERS:
                del config.MASTERS[chat_id]
            config.PLAYERS.update({chat_id: InfectedPlayer(name)})
            set_commands(chat_id, config.PLAYER_COMMANDS)
            bot.send_message(message.chat.id, '@%s is known as player %s' % (username, name))
            bot.send_message(chat_id,
                             'Hello, @%s! You are now known here as a player! Your role name %s' % (username, name))
        except utilities.UtilitiesError as err:
            bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (player, err))
            bot.register_next_step_handler(message, do_add_player)
        except config.PrivacyError as err:
            bot.send_message(message.chat.id, err)


@bot.message_handler(commands=['set_sick'])
@only_master_wrapper
def set_sick_command(message):
    bot.send_message(message.chat.id, 'Type players usernames and disease name as "username1 name1; username2 name2; ..."')
    bot.register_next_step_handler(message, do_set_sick)


def set_disease(username: str, disease: Disease, master_id: int):
    player_id = config.get_id(username)
    player = config.PLAYERS.get(player_id, None)
    if player is None:
        bot.send_message(master_id, '@%s is not known as a player' % username)
    else:
        player.set_sick(disease, time.time())
        Notifier.send_symptom_regularly(player_id, player)
        bot.send_message(master_id, '@%s is now sick with %s' % (username, disease.name))


def do_set_sick(message):
    players = message.text.split(';')
    for player in players:
        try:
            username, disease_name = utilities.split_string(player, 2)
            disease = config.DISEASES.get(disease_name, None)
            if disease is None:
                bot.send_message(message.chat.id, '%s is not known as a disease' % disease_name)
            else:
                set_disease(username, disease, message.chat.id)
        except config.PrivacyError as err:
            bot.send_message(message.chat.id, err)


@bot.message_handler(commands=['set_rnd_sick'])
@only_master_wrapper
def set_rnd_sick_command(message):
    bot.send_message(message.chat.id, 'Type players usernames as "name1 name2 name3"')
    bot.register_next_step_handler(message, do_set_rnd_sick)


def do_set_rnd_sick(message):
    players = utilities.split_string(message.text)
    if players == ['all']:
        players = config.PLAYERS.keys()
    disease = random.choice(list(config.DISEASES.values()))
    for player in players:
        try:
            username = config.get_id(player)
            set_disease(username, disease, message.chat.id)
        except config.PrivacyError as err:
            bot.send_message(message.chat.id, err)


@bot.message_handler(commands=['set_healthy'])
@only_master_wrapper
def set_healthy_command(message):
    bot.send_message(message.chat.id, 'Type players usernames as "name1 name2 name3"')
    bot.register_next_step_handler(message, do_set_healthy)


def do_set_healthy(message):
    players = utilities.split_string(message.text)
    if players == ['all']:
        players = config.PLAYERS.keys()
    for player_id in players:
        try:
            username = config.get_id(player_id)
            player = config.PLAYERS.get(player_id, None)
            if player is None:
                bot.send_message(message.chat.id, '@%s is not known as a player' % username)
            elif player.is_dead():
                bot.send_message(message.chat.id,
                            '@%s role %s is already dead. Use add_player command to revoke' % (username, player.name))
            elif not player.is_sick():
                bot.send_message(message.chat.id, '@%s role %s is already healthy' % (username, player.name))
            else:
                player.set_healthy()
                Notifier.send_symptom(player_id, player)
                Notifier.stop_notify(player_id)
                bot.send_message(message.chat.id, '@%s role %s is healthy now' % (username, player.name))
                bot.send_message(player_id, '%s, you are healthy now!' % player.name)
        except utilities.UtilitiesError as err:
            bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (player_id, err))
            bot.register_next_step_handler(message, do_set_healthy)


@bot.message_handler(commands=['set_healer'])
@only_master_wrapper
def set_healer_command(message):
    bot.send_message(message.chat.id, 'Type players usernames as "name1 name2 name3"')
    bot.register_next_step_handler(message, do_set_healer)


def do_set_healer(message):
    players = utilities.split_string(message.text)
    if players == ['all']:
        players = config.PLAYERS.keys()
    for player_id in players:
        try:
            username = config.get_id(player_id)
            player = config.PLAYERS.get(player_id, None)
            if player is None:
                bot.send_message(message.chat.id, '@%s is not known as a player' % username)
            elif player.is_healer:
                bot.send_message(message.chat.id,
                                 '@%s role %s is already a healer' % (username, player.name))
            else:
                player.is_healer = True
                set_commands(player_id, config.HEALER_COMMANDS)
                bot.send_message(message.chat.id,
                                 '@%s role %s is a healer' % (username, player.name))
                bot.send_message(player_id,
                                 '%s, you are a healer' % player.name)
        except config.PrivacyError as err:
            bot.send_message(message.chat.id, err)


@bot.message_handler(commands=['del_healer'])
@only_master_wrapper
def del_healer_command(message):
    bot.send_message(message.chat.id, 'Type players usernames as "name1 name2 name3"')
    bot.register_next_step_handler(message, do_del_healer)


def do_del_healer(message):
    players = utilities.split_string(message.text)
    if players == ['all']:
        players = config.PLAYERS.keys()
    for player_id in players:
        try:
            username = config.get_id(player_id)
            player = config.PLAYERS.get(player_id, None)
            if player is None:
                bot.send_message(message.chat.id, '@%s is not known as a player' % username)
            elif not player.is_healer:
                bot.send_message(message.chat.id,
                                 '@%s role %s is already not a healer' % (username, player.name))
            else:
                player.is_healer = False
                set_commands(player_id, config.PLAYER_COMMANDS)
                bot.send_message(message.chat.id,
                                 '@%s role %s is not a healer' % (username, player.name))
                bot.send_message(player_id,
                             '%s, you are not a healer' % player.name)
        except config.PrivacyError as err:
            bot.send_message(message.chat.id, err)


@bot.message_handler(commands=['stop_notify'])
@only_master_wrapper
def stop_notify_command(message):
    bot.send_message(message.chat.id,
                     'Type players usernames as "name1 name2 name3". Type "all" to stop notifications to all players')
    bot.register_next_step_handler(message, do_stop_notify)


def do_stop_notify(message):
    usernames = utilities.split_string(message.text)
    if usernames == ['all']:
        usernames.clear()
        for player_id in config.PLAYERS:
            usernames.append(config.get_username(player_id))
    for username in usernames:
        player_id = config.get_id(username)
        Notifier.stop_notify(player_id)
        role_name = 'no role'
        player = config.PLAYERS.get(player_id, None)
        if player is not None:
            role_name = player.name
        bot.send_message(message.chat.id,
                     'Stopped notifications for @%s, with role: %s' % (username, role_name))


@bot.message_handler(commands=['add_diseases'])
@only_master_wrapper
def add_diseases_command(message):
    bot.send_message(message.chat.id,
                     'Send a json file with diseases')
    bot.register_next_step_handler(message, do_add_diseases)


def do_add_diseases(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    try:
        for disease in disease_reader.from_multistr(downloaded_file):
            config.DISEASES[disease.name] = disease
    except disease_reader.ReaderError as err:
        bot.send_message(message.chat.id, 'Invalid input %s' % str(err))
    except json.JSONDecodeError as err:
        bot.send_message(message.chat.id, 'Invalid json')
    bot.send_message(message.chat.id,
                     'Ok, diseases list updated from your file. Now we have %s' % str(config.DISEASES.keys()))


@bot.message_handler(commands=['set_diseases'])
@only_master_wrapper
def set_diseases_command(message):
    bot.send_message(message.chat.id,
                     'Send a json file with diseases')
    bot.register_next_step_handler(message, do_set_diseases)


def do_set_diseases(message):
    config.DISEASES.clear()
    do_add_diseases(message)


@bot.message_handler(commands=['reset_diseases'])
@only_master_wrapper
def reset_diseases_command(message):
    config.reset_diseases()
    bot.send_message(message.chat.id,
                     'Ok, diseases were reset to default. Now we have %s' % str(config.DISEASES.keys()))
