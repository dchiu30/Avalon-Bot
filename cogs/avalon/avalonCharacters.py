from enum import Enum

class Character():
    def __init__(self):
        self.name = ""
        self.isGood = True
        self.sees = []

class Assassin(Character):
    def __init__(self):
        self.name = "Assassin"
        self.isGood = False
        self.sees = [Minion,Mordred,Morgana]

class Merlin(Character):
    def __init__(self):
        self.name = "Merlin"
        self.isGood = True
        self.sees = [Assassin, Minion, Morgana, Oberon]

class Minion(Character):
    def __init__(self):
        self.name = "Minion"
        self.isGood = False
        self.sees = [Assassin, Mordred, Morgana]

class Mordred(Character):
    def __init__(self):
        self.name = "Mordred"
        self.isGood = False
        self.sees = [Assassin,Minion,Morgana]

class Morgana(Character):
    def __init__(self):
        self.name = "Morgana"
        self.isGood = False
        self.sees = [Assassin, Minion, Mordred]

class Oberon(Character):
    def __init__(self):
        self.name = "Oberon"
        self.isGood = False

class Percival(Character):
    def __init__(self):
        self.name = "Percival"
        self.isGood = True
        self.sees = [Merlin, Morgana]

class Servant(Character):
    def __init__(self):
        self.name = "Servant"
        self.isGood = True