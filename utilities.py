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

def format_id_name(name: str, chat_id:int):
    return '%s: %i\n' % (name, chat_id)



def get_id(id_str: str):
    id_str = id_str.strip()
    if not id_str.isnumeric():
        raise UtilitiesError('Wrong input for id "%s"' % id_str)
    return int(id_str)

def get_id_name(name_id: str):
    parts = list(filter(lambda a: a!='', name_id.strip().split(' ')))
    if len(parts) != 2:
        raise UtilitiesError('Wrong input for "name id" string for "%s"' % name_id)
    if parts[1].isnumeric():
        name = parts[0]
        chat_id = int(parts[1])
    elif parts[0].isnumeric():
        name = parts[1]
        chat_id = int(parts[0])
    else:
        raise UtilitiesError('Wrong input for "name id" string for "%s"' % name_id)
    return name, chat_id




