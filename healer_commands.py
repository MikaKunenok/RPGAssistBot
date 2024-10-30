import telebot
import time

from the_bot import bot
import config
import utilities


def only_healer_query_wrapper(func):
    def wrap(query):
        if query.message.chat.id in config.PLAYERS:
            if config.PLAYERS[query.message.chat.id].is_healer:
                func(query)
            else:
                bot.send_message(query.message.chat.id, 'You are not allowed to do it')
        else:
            bot.send_message(query.message.chat.id, 'You are not known as a player here')

    return wrap


def only_healer_wrapper(func):
    def wrap(message):
        if message.chat.id in config.PLAYERS:
            if config.PLAYERS[message.chat.id].is_healer:
                func(message)
            else:
                bot.send_message(message.chat.id, 'You are not allowed to do it')
        else:
            bot.send_message(message.chat.id, 'You are not known as a player here')

    return wrap


@bot.message_handler(commands=['test'])
@only_healer_wrapper
def test_command(message):
    bot.send_message(message.chat.id,
                     'What player do you want to test? Type his/her username\n'
                    )
    bot.register_next_step_handler(message, send_test_keyboard)


def send_test_keyboard(message):
    try:
        username = utilities.clear(message.text)
        player_id = config.get_id(username)
        player = config.PLAYERS.get(player_id, None)
        if player is None:
            bot.send_message(message.chat.id, '@%i is not known as player' % username)
        else:
            if player.is_dead():
                bot.send_message(message.chat.id, 'Sorry, @%s(%s) is already dead' % (username, player.name))
            elif player.is_sick():
                keyboard = telebot.types.InlineKeyboardMarkup()
                for test_name in player.disease.current_test_names(time.time()):
                    keyboard.add(telebot.types.InlineKeyboardButton(
                                 test_name, callback_data='%i %s' % (player_id, test_name)))
                bot.send_message(message.chat.id, 'What do you want to test for %s?' % player.name, reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, '%s is healthy' % player.name)
    except utilities.UtilitiesError as err:
        bot.send_message(message.chat.id, 'Invalid input at "%s".\n%s\n Try again' % (message.text, err))
        bot.register_next_step_handler(message, send_test_keyboard)
    except config.PrivacyError as err:
        bot.send_message(message.chat.id, err)


@bot.callback_query_handler(func=lambda call: True)
@only_healer_query_wrapper
def test_keyboard_handler(query):
    try:
        player_id, test_name= utilities.split_string(query.data, 2)
        player = config.PLAYERS.get(player_id, None)
        username = config.get_username(player_id)
        if player is None:
            bot.send_message(query.message.chat.id, '@%s is not known as player' % username)
        else:
            bot.send_message(query.message.chat.id, '%s test is:\n%s' % (test_name, player.test(test_name)))
    except utilities.UtilitiesError as err:
        bot.send_message(query.message.chat.id, 'Invalid input from keyboard "%s".\n%s\n Try again' % (query.message.text, err))
    except config.PrivacyError as err:
        bot.send_message(query.message.chat.id, err)
