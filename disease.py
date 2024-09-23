# class Disease implements mechanics from
# https://docs.google.com/document/d/1V78lwOSnsDeoXex329XXh7I379fNMcIvODqNJy-rUyo

from utilities import get_symptom_at, periods_from_start, clear

UNDEFINED: str = 'undefined'

HEALED = 'healed'
PROGRESS = 'progress'
DELAY = 'delay'
NO_EFFECT = 'no effect'
DEAD = 'dead'
TREAT_RESULTS = [DEAD, NO_EFFECT, PROGRESS, DELAY, HEALED, UNDEFINED]

GOOD = "good"
BAD = "bad"
TEST_RESULTS = [GOOD, BAD, UNDEFINED]

class DiseaseError(EnvironmentError):
    pass

class Disease:
    # describes the disease that appears at the game.
    # The Disease object can tell you what and when happens to an infected person
    # but it does not track the status of the person. For that use class InfectedHuman
    def __init__(self, period: int, name: str, treats: dict, deadly: bool, stages: list):
        # give the disease a name
        # define treats as {potion_code: result}
        # define the course of the disease as lists in args
        # each list defines next hour stage (symptom, {test_name: result})
        symptoms = []
        tests = []
        the_treats = {}
        for stage in stages:
            if not isinstance(stage, list) and len(stage) != 2:
                raise DiseaseError("Disease '%s' has not a proper list in disease course %s" % (name, stage))
            symptoms.append(stage[0])
            if not isinstance(stage[1], dict):
                raise DiseaseError("Disease '%s' has not a proper tests in disease course %s" % (name, stage[1]))
            the_test = {}
            for test_name, result in stage[1].items():
                test_name = clear(test_name)
                if test_name in the_test:
                    raise DiseaseError("Disease '%s' has rewritten test result for '%s'" % (name, test_name))
                result = clear(result)
                if result not in TEST_RESULTS:
                    raise DiseaseError(
                        "Disease '%s' has unknown test result for '%s' : %s. Should be in %s" % (name, test_name, result, TEST_RESULTS))
                the_test[test_name] = result
            tests.append(the_test)
        for potion, result in treats.items():
            potion = clear(potion)
            if potion in the_treats:
                raise DiseaseError("Disease '%s' has rewritten treat result for '%s'" % (name, potion))
            result = clear(result)
            if result not in TREAT_RESULTS:
                raise DiseaseError("Disease '%s' has unknown treat result for potion '%s' : %s. Should be in %s" % (name, potion, result, TREAT_RESULTS))
            the_treats[potion] = result
        self.__symptoms = symptoms
        self.__stages_num = len(symptoms)
        self.__deadly = deadly
        self.__treats = treats
        self.__tests = tests
        self.name = clear(name)
        self.__period = period

    def period(self):
        return self.__period

    def check_death(self, infection_time: float):
        if self.__deadly:
            infected_for = periods_from_start(infection_time, self.__period)
            if infected_for >= self.__stages_num:
                return True
        return False

    def get_symptom(self, infection_time: float):
        # find out what does the person, infected since infection_time
        #    should feel at current_time
        infected_for = periods_from_start(infection_time, self.__period)
        return get_symptom_at(self.__symptoms, infected_for)

    def treat(self, potion: str):
        # find out what should be the result of treating the infected person with potion
        return self.__treats.get(clear(potion), UNDEFINED)

    def __get_current_tests(self, infection_time: float):
        infected_for = periods_from_start(infection_time, self.__period)
        return get_symptom_at(self.__tests, infected_for)

    def current_test_names(self, infection_time: float):
        test_results = self.__get_current_tests(infection_time)
        return test_results.keys()

    def test(self, test_name: str, infection_time: float):
        # test in person infected since infection_time for test_name
        test_results = self.__get_current_tests(infection_time)
        return test_results.get(clear(test_name), UNDEFINED)