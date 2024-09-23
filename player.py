class Player:
    def __init__(self, name: str, is_healer: bool = False):
        self.name = name
        self.is_healer = is_healer
        self.__is_dead = False
