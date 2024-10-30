# some useful functions for disease implementation

import time

class UtilitiesError(EnvironmentError):
    pass

def periods_from_start(start_time: float, period: int):
    print(time.time())
    print(start_time)
    pass
    time_from_infection = time.time() - start_time
    return int(time_from_infection / period)


def get_symptom_at(symptoms: list, infected_for: int):
    # this function detects what happens
    # to a person infected for infected_for periods
    # according to a list of possible symptoms
    stages_num = len(symptoms)
    result = None
    if infected_for >= stages_num:
        result = symptoms[stages_num - 1]
    else:
        for hour in range(stages_num, -1, -1):
            if infected_for >= hour:
                result = symptoms[hour]
                break
    return result


def clear(string: str):
    return string.lower().strip()


def split_string(my_str: str, parts_num=None):
    parts = list(filter(lambda a: a!='', my_str.strip().split(' ')))
    if parts_num is not None and len(parts) != parts_num:
        raise UtilitiesError('Cannot split "%s" in %i parts' % (my_str, parts_num))
    return parts


