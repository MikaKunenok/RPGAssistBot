import telebot
import config
bot = telebot.TeleBot(config.TOKEN)

def set_commands(chat_id, commands: dict):
    the_commands = []
    for name, description in commands.items():
        the_commands.append(telebot.types.BotCommand(name, description))
    bot.set_my_commands(commands=the_commands, scope=telebot.types.BotCommandScopeChat(chat_id))


def send_help_message(chat_id, commands: dict):
    help_message = ''
    for cmd, description in commands.items():
        help_message += '%s : %s\n' % (cmd, description)
    bot.send_message(chat_id, help_message)