import schedule
import telebot

from the_bot import bot
from infected_player import InfectedPlayer


class NotifierClass:
    def __init__(self, the_bot: telebot.TeleBot):
        self.__jobs = {}
        self.__bot = the_bot

    def send_symptom(self, chat_id: int, player: InfectedPlayer):
        if player.is_dead():
            self.__bot.send_message(chat_id, 'You are already dead, sorry')
            self.stop_notify(chat_id)
        elif player.is_sick():
            self.__bot.send_message(
                chat_id,
                'Your symptom now is \n' +
                player.get_symptom()
            )
        else:
            self.__bot.send_message(
                chat_id,
                'You are already healthy!'
            )
            self.stop_notify(chat_id)

    def send_symptom_regularly(self, chat_id: int, player: InfectedPlayer):
        self.send_symptom(chat_id, player)

        def notify():
            self.send_symptom(chat_id, player)

        if chat_id not in self.__jobs:
            self.__jobs[chat_id] = []

        self.__jobs[chat_id].append(schedule.every(player.disease.period()).seconds.do(notify))

    def stop_notify(self, chat_id: int):
        if chat_id in self.__jobs:
            for job in self.__jobs[chat_id]:
                schedule.cancel_job(job)
            del self.__jobs[chat_id]

Notifier = NotifierClass(the_bot)
