import random
import json
from .avalonPlayer import AvalonPlayer
from .avalonCharacters import Assassin, Merlin, Minion, Mordred, Morgana, Oberon, Percival, Servant

class AvalonEngine:

    @staticmethod
    def fetchGameSetup(playerCount):
        with open("gameSetup.json",'r') as f:
            gameSetup = json.load(f)
        return gameSetup[str(playerCount)]

    @staticmethod
    def genCharacterList(goodCount, badCount, specialCharacters):
        characters = [Assassin,Merlin]
        goodCount -= 1
        badCount -= 1
        for character in specialCharacters:
            characters.append(character)
            if character.isGood:
                goodCount -= 1
            else:
                badCount -=1
        for i in range(goodCount):
            characters.append(Servant)
        for i in range(badCount):
            characters.append(Minion)
        return characters

    @staticmethod
    def assignCharacters(users, characters):
        random.shuffle(characters)
        players = []
        for i in range(len(users)):
            players.append(AvalonPlayer(users[i]))
            players[i].assignCharacter(characters.pop())
        return players

    @staticmethod
    def genCharacterMap(players):
        characterMap = {}
        for player in players:
            characterName = player.character.name
            if(characterName in characterMap.keys()):
                characterMap[characterName].append(player.user)
            else:
                characterMap[characterName] = player.user
        return characterMap

    @staticmethod
    def revealCharacters(character, characterMap):
        revealedCharacters = []
        for revealed in character.sees:
            revealedCharacters += characterMap[revealed]
        return random.shuffle(revealedCharacters)

    @staticmethod
    def isTeamApproved(votes):
        decision = 0
        for vote in votes:
            decision = (decision+1) if vote else (decision-1)
        if decision > 0:
            return True
        return False

    @staticmethod
    def doesQuestPass(questDecisions):
        return all(questDecisions)

    @staticmethod
    def doesQuestThreePass(questDecisions):
        votes = 0
        for decision in questDecisions:
            votes = (votes + 1) if (~decision) else votes
        if votes < 2:
            return  True
        return False
