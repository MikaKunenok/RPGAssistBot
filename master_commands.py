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
    bot.send_message(message.chat.id, 'Type master chat id and name as "name id"')
    bot.register_next_step_handler(message, do_add_master)


def do_add_master(message):
    try:
        name, chat_id = utilities.get_id_name(message.text)
        name = name.strip()
        chat_id = int(chat_id)
        if chat_id in config.PLAYERS:
            del config.PLAYERS[chat_id]
        config.MASTERS.update({chat_id: name})
        set_commands(chat_id, config.MASTER_COMMANDS)
        bot.send_message(message.chat.id, '%i is known as master %s' % (chat_id, name))
        bot.send_message(chat_id, 'Hello, %s! You are now known here as a master!' % name)
    except utilities.UtilitiesError as err:
        bot.send_message(message.chat.id, 'Invalid input.\n%s\n Try again' % err)
        bot.register_next_step_handler(message, do_add_master)


@bot.message_handler(commands=['del_master'])
@only_master_wrapper
def del_master(message):
    bot.send_message(message.chat.id, 'Type masters chat ids as "id1; id2; id3..."')
    bot.register_next_step_handler(message, do_del_master)


def do_del_master(message):
    masters = message.text.split(';')
    for master in masters:
        try:
            chat_id = utilities.get_id(master)
            if chat_id in config.MASTERS:
                del config.MASTERS[chat_id]
                bot.send_message(message.chat.id, '%i is not a master any more' % chat_id)
                bot.send_message(chat_id, 'Hello! You was deleted from masters, sorry')
            else:
                bot.send_message(message.chat.id, '%i was not a master ever' % chat_id)
        except utilities.UtilitiesError as err:
            bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (master, err))
            bot.register_next_step_handler(message, do_del_master)


@bot.message_handler(commands=['set_masters'])
@only_master_wrapper
def set_masters_command(message):
    bot.send_message(message.chat.id,
                     'Type masters names and chat ids as\n' +
                     'name1 id1; name2 id2'
                     )
    bot.register_next_step_handler(message, do_set_masters)


def do_set_masters(message):
    masters = message.text.split(';')
    for master in masters:
        try:
            name, chat_id = utilities.get_id_name(master)
            config.MASTERS.update({chat_id: name})
            set_commands(chat_id, config.MASTER_COMMANDS)
            bot.send_message(message.chat.id, '%i is known as master %s' % (chat_id, name))
            bot.send_message(chat_id, 'Hello, %s! You are now known here as a master!' % name)
        except utilities.UtilitiesError as err:
            bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (master, err))
            bot.register_next_step_handler(message, do_set_masters)


@bot.message_handler(commands=['list_players'])
@only_master_wrapper
def list_players_command(message):
    for chat_id, player in config.PLAYERS.items():
        notify = '%i named %s\n' % (chat_id, player.name)
        if player.is_dead():
            notify += 'Is dead\n'
        elif player.is_sick():
            notify += 'Sick with %s\n' % player.disease.name
        else:
            notify += 'Healthy\n'
        if player.is_healer:
            notify += 'Is healer'
        bot.send_message(message.chat.id, notify)


@bot.message_handler(commands=['add_player'])
@only_master_wrapper
def add_player(message):
    bot.send_message(message.chat.id, 'Type players chat id and name as "name1 id1; name2 id2; ..."')
    bot.register_next_step_handler(message, do_add_player)


def do_add_player(message):
    players = message.text.split(';')
    for player in players:
        try:
            name, chat_id = utilities.get_id_name(player)
            if chat_id in config.MASTERS:
                del config.MASTERS[chat_id]
            config.PLAYERS.update({chat_id: InfectedPlayer(name)})
            set_commands(chat_id, config.PLAYER_COMMANDS)
            bot.send_message(message.chat.id, '%i is known as player %s' % (chat_id, name))
            bot.send_message(chat_id, 'Hello, %s! You are now known here as a player!' % name)
        except utilities.UtilitiesError as err:
            bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (player, err))
            bot.register_next_step_handler(message, do_add_player)


@bot.message_handler(commands=['set_sick'])
@only_master_wrapper
def set_sick_command(message):
    bot.send_message(message.chat.id, 'Type players chat ids and disease name as "id1 name1; id2 name2; ..."')
    bot.register_next_step_handler(message, do_set_sick)


def set_disease(player_id: int, disease: Disease, master_id: int):
    player = config.PLAYERS.get(player_id, None)
    if player is None:
        bot.send_message(master_id, '%i is not known as a player' % player_id)
    else:
        player.set_sick(disease, time.time(), player_id, bot)
        Notifier.send_symptom_regularly(player_id, player)
        bot.send_message(master_id, '%i is now sick with %s' % (player_id, disease.name))


def do_set_sick(message):
    players = message.text.split(';')
    for player in players:
        try:
            disease_name, chat_id = utilities.get_id_name(player)
            disease = config.DISEASES.get(disease_name, None)
            if disease is None:
                bot.send_message(message.chat.id, '%s is not known as a disease' % disease_name)
            else:
                set_disease(chat_id, disease, message.chat.id)
        except utilities.UtilitiesError as err:
            bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (player, err))
            bot.register_next_step_handler(message, do_set_sick)

@bot.message_handler(commands=['set_rnd_sick'])
@only_master_wrapper
def set_rnd_sick_command(message):
    bot.send_message(message.chat.id, 'Type players chat ids as "id1; id2; ..."')
    bot.register_next_step_handler(message, do_set_rnd_sick)


def do_set_rnd_sick(message):
    if utilities.clear(message.text) == 'all':
        players = config.PLAYERS.keys()
    else:
        players = message.text.split(';')
    disease = random.choice(list(config.DISEASES.values()))
    for player in players:
        try:
            chat_id = utilities.get_id(player)
            set_disease(chat_id, disease, message.chat.id)
        except utilities.UtilitiesError as err:
            bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (player, err))
            bot.register_next_step_handler(message, do_set_rnd_sick)


@bot.message_handler(commands=['set_healthy'])
@only_master_wrapper
def set_healthy_command(message):
    bot.send_message(message.chat.id, 'Type players chat ids as "id1; id2; ..."')
    bot.register_next_step_handler(message, do_set_healthy)


def do_set_healthy(message):
    players = message.text.split(';')
    for player_id in players:
        try:
            chat_id = utilities.get_id(player_id)
            player = config.PLAYERS.get(chat_id, None)
            if player is None:
                bot.send_message(message.chat.id, '%i is not known as a player' % chat_id)
            elif player.is_dead():
                bot.send_message(message.chat.id,
                                 '%i player is already dead. Use add_player command to revoke' % chat_id)
            elif not player.is_sick():
                bot.send_message(message.chat.id, '%i player is already healthy' % chat_id)
            else:
                player.set_healthy()
                Notifier.send_symptom(player_id, player)
                Notifier.stop_notify(player_id)
                bot.send_message(message.chat.id, '%i , known as %s,  is healthy now' % (chat_id, player.name))
                bot.send_message(chat_id, '%s, you are healthy now!' % player.name)
        except utilities.UtilitiesError as err:
            bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (player_id, err))
            bot.register_next_step_handler(message, do_set_healthy)


@bot.message_handler(commands=['set_healer'])
@only_master_wrapper
def set_healer_command(message):
    bot.send_message(message.chat.id, 'Type players chat ids as "id1; id2.."')
    bot.register_next_step_handler(message, do_set_healer)


def do_set_healer(message):
    players = message.text.split(';')
    for player_id in players:
        try:
            chat_id = utilities.get_id(player_id)
            if chat_id in config.MASTERS:
                del config.MASTERS[chat_id]
            player = config.PLAYERS.get(chat_id, None)
            if player is None:
                bot.send_message(message.chat.id, '%i is not known as a player' % chat_id)
            elif player.is_healer:
                bot.send_message(message.chat.id,
                                 '%i, known as %s, is already a healer' % (chat_id, player.name))
            else:
                config.PLAYERS[chat_id].is_healer = True
                set_commands(chat_id, config.HEALER_COMMANDS)
                bot.send_message(message.chat.id,
                                 '%i, known as %s, is a healer' % (chat_id, player.name))
                bot.send_message(chat_id,
                                 '%i, you are a healer' % player.name)
        except utilities.UtilitiesError as err:
            bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (player_id, err))
            bot.register_next_step_handler(message, do_set_healer)


@bot.message_handler(commands=['del_healer'])
@only_master_wrapper
def del_healer_command(message):
    bot.send_message(message.chat.id, 'Type players chat ids as "id1; id2..."')
    bot.register_next_step_handler(message, do_del_healer)


def do_del_healer(message):
    players = message.text.split(';')
    for player_id in players:
        try:
            chat_id = utilities.get_id(player_id)
            player = config.PLAYERS.get(chat_id, None)
            if player is None:
                bot.send_message(message.chat.id, '%i is not known as a player' % chat_id)
            elif not player.is_healer:
                bot.send_message(message.chat.id,
                                 '%i, known as %s, is already not a healer' % (chat_id, player.name))
            else:
                config.PLAYERS[chat_id].is_healer = False
                set_commands(chat_id, config.PLAYER_COMMANDS)
                bot.send_message(message.chat.id,
                                 '%i, known as %s, is a healer' % (chat_id, player.name))
                bot.send_message(message.chat.id,
                                 '%i, known as %s, is not a healer' % (chat_id, player.name))
        except utilities.UtilitiesError as err:
            bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (player_id, err))
            bot.register_next_step_handler(message, do_del_healer)


@bot.message_handler(commands=['stop_notify'])
@only_master_wrapper
def stop_notify_command(message):
    bot.send_message(message.chat.id,
                     'Type players chat id as "id1; id2; id3...". Type "all" to stop notifications to all players')
    bot.register_next_step_handler(message, do_stop_notify)


def do_stop_notify(message):
    mes = utilities.clear(message.text)
    players = {}
    if mes == 'all':
        players = config.PLAYERS
    else:
        for pid in mes.split(';'):
            try:
                player_id = utilities.get_id(pid)
                player = config.PLAYERS.get(player_id, None)
                if player is None:
                    bot.send_message(message.chat.id,
                             '%i is not known as player' % player_id)
                else:
                    players[player_id] = player
                for pid, player in players.items():
                    pass
                bot.send_message(message.chat.id,
                                 'Could stop for %i players, but not implemented yet' % len(players.keys()))
            except utilities.UtilitiesError as err:
                bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (pid, err))
                bot.register_next_step_handler(message, do_stop_notify)


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
                     'Ok, diseases were reseed to default. Now we have %s' % str(config.DISEASES.keys()))
