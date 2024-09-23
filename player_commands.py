import time
import random

from the_bot import bot
import config
from player_notifier import Notifier

def only_player_wrapper(func):
    def wrap(message):
        if message.chat.id in config.PLAYERS:
            func(message)
        else:
            bot.send_message(message.chat.id,
                             'You are not known as a player here.\\n' +
                             'Ask a master to add you. Use \\list_masters to know their ids')
    return wrap


@bot.message_handler(commands=['sick'])
@only_player_wrapper
def sick_command(message):
    player = config.PLAYERS[message.chat.id]
    if player.is_sick():
        bot.send_message(message.chat.id, 'Yes, you are already sick. ' +
                                          'Use \\symptom to know your condition')
    else:
        the_disease = random.choice(list(config.DISEASES.values()))
        bot.send_message(message.chat.id,'Oh, It\'s sad!' )
        player.set_sick(the_disease, time.time(), message.chat.id, bot)
        Notifier.send_symptom_regularly(message.chat.id, player)


@bot.message_handler(commands=['symptom'])
@only_player_wrapper
def symptom_command(message):
    player = config.PLAYERS[message.chat.id]
    Notifier.send_symptom(message.chat.id, player)


@bot.message_handler(commands=['treat'])
@only_player_wrapper
def treat_command(message):
    bot.send_message(message.chat.id, 'Type the potion name')
    bot.register_next_step_handler(message, do_treat)


@only_player_wrapper
def do_treat(message):
    bot.send_message(
        message.chat.id,
        'Oh, let me see...'
    )
    player = config.PLAYERS[message.chat.id]
    player.treat(message.text)
    Notifier.send_symptom(message.chat.id, player)

@bot.message_handler(commands=['stop'])
@only_player_wrapper
def stop_command(message):
    Notifier.stop_notify(message.chat.id)
    bot.send_message(message.chat.id, 'Ok, you will not be notified about your condition')
