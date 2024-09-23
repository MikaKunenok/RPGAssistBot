import telebot

import config
from the_bot import bot, set_commands, send_help_message
import utilities

@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(
        'Disease Rules',
        url=config.RULES_URL
        )
    )
    bot.send_message(
        chat_id,
        'Greetings!\n' +
        'This bot makes your roleplay at the polygon easier.\n' +
        'And automates some game-master\'s work.\n' +
        'Currently this bot holds Disease mechanics,\n click the button to see the rules -\n',
        reply_markup=keyboard,
    )
    if chat_id in config.MASTERS:
        bot.send_message(
            chat_id,
            '%s, you are known as master' % config.MASTERS[chat_id]
        )
        set_commands(chat_id, config.MASTER_COMMANDS)
    elif chat_id in config.PLAYERS:
        player = config.PLAYERS[chat_id]
        bot.send_message(
            chat_id,
            '%s, you are known as player' % player.name
        )
        if player.is_healer:
            set_commands(chat_id, config.HEALER_COMMANDS)
            bot.send_message(
                chat_id,
                'You are a healer, by the way'
            )
        else:
            set_commands(chat_id, config.HEALER_COMMANDS)
    else:
        bot.send_message(
            chat_id,
            'You are not known as a player or master. Ask any master to add you\n' +
            'Use list_masters command to find them'
        )


@bot.message_handler(commands=['help'])
def help_command(message):
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(
        'Message the developer', url='telegram.me/' + config.DEVELOPER
        )
    )
    if chat_id in config.MASTERS:
        bot.send_message(
            chat_id,
            'With this bot you can administrate the game -\n' +
            'register masters and players, set players roles, ' +
            'set players diseases and edit diseases list'
        )
        send_help_message(chat_id, config.MASTER_COMMANDS)
    elif chat_id in config.PLAYERS:
        player = config.PLAYERS[chat_id]
        if player.is_healer:
            bot.send_message(chat_id,
                             'With this bot you can track your disease and treat it.\n' +
                             'You can also test other players to find proper treat for them')
            send_help_message(chat_id, config.HEALER_COMMANDS)
        else:
            bot.send_message(chat_id, 'With this bot you can track your disease and treat it')
            send_help_message(chat_id, config.PLAYER_COMMANDS)


@bot.message_handler(commands=['list_masters'])
def list_masters_command(message):
    notify = ''
    for chat_id, name in config.MASTERS.items():
        notify += utilities.format_id_name(name, chat_id) + '\n'
    bot.send_message(message.chat.id, notify)

@bot.message_handler(commands=['im_master'])
def immaster_command(message):
    if message.chat.id in config.MASTERS:
        bot.send_message(message.chat.id, 'Yes, I know :)')
    else:
        bot.send_message(message.chat.id, 'Type master password')
        bot.register_next_step_handler(message, get_master_pass)


def get_master_pass(message):
    bot.send_message(
        message.chat.id,
        'Ok, let me see...'
    )
    notify = 'Password is wrong'
    if message.text == config.MASTER_PASS:
        bot.register_next_step_handler(message, get_master_name)
        notify = 'Password is right! Type your name'
    bot.send_message(message.chat.id, notify)


def get_master_name(message):
    config.MASTERS.update({message.chat.id: message.text})
    bot.send_message(message.chat.id, '%s, welcome to masters!' % message.text)

