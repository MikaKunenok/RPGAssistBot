# InfectedPlayer class implements mechanics from
# https://docs.google.com/document/d/1V78lwOSnsDeoXex329XXh7I379fNMcIvODqNJy-rUyo

from player import Player
from disease import Disease
from disease import PROGRESS, DELAY, HEALED, NO_EFFECT, UNDEFINED, DEAD


def is_sick_wrapper(default):
    def wrapper(func):
        def wrap(*args, **kwargs):
            if args[0].disease is not None:
                return func(*args, **kwargs)
            else:
                return default

        return wrap

    return wrapper


class InfectedPlayer(Player):
    # use an instance of InfectedHuman for tracking the status of a person, infected with some Disease
    # InfectedHuman does not do any changes to the Disease
    def __init__(self, name: str, is_healer: bool = False):
        super().__init__(name, is_healer)
        self.disease = None
        self.__disease_start = None
        self.__disease_delay = 0
        self.__is_dead = False
        self.__jobs = []

    @property
    def disease_start(self):
        return self.__disease_start

    @is_sick_wrapper(default=None)
    def effective_disease_start(self):
        return self.__disease_start + self.__disease_delay

    def set_sick(self, the_disease: Disease, start_time: float):
        self.disease = the_disease
        self.__disease_start = start_time

    def set_healthy(self):
        self.disease = None
        self.__disease_start = None
        self.__disease_delay = 0

    @is_sick_wrapper(default=UNDEFINED)
    def get_symptom(self):
        self.__is_dead = self.disease.check_death(self.effective_disease_start())
        return self.disease.get_symptom(self.effective_disease_start())

    @is_sick_wrapper(default=UNDEFINED)
    def treat(self, potion):
        treat_result = NO_EFFECT
        if not self.is_dead:
            treat_result = self.disease.treat(potion)
            if treat_result == PROGRESS:
                self.__disease_delay -= - self.disease.period()
            elif treat_result == DELAY:
                self.__disease_delay += self.disease.period()
            elif treat_result == UNDEFINED or treat_result == NO_EFFECT:
                pass
            elif treat_result == HEALED:
                self.set_healthy()
            elif treat_result == DEAD:
                self.__is_dead = True
                self.stop_notify()
        return treat_result

    @is_sick_wrapper(default=UNDEFINED)
    def test(self, test_name):
        return self.disease.test(test_name, self.effective_disease_start())

    def is_sick(self):
        return self.disease is not None

    @is_sick_wrapper(default=False)
    def is_dead(self):
        self.__is_dead = self.__is_dead or self.disease.check_death(self.effective_disease_start())
        return self.__is_dead
