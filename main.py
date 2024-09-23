import time
import schedule
from threading import Thread

from the_bot import bot
import default_commands
import master_commands
import healer_commands
import player_commands


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)


Thread(target=schedule_checker).start()

bot.polling(none_stop=True)
