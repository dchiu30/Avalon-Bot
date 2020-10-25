from .avalon.avalonCharacters import Assassin, Merlin, Minion, Mordred, Morgana, Oberon, Percival, Servant
from .avalon.avalonEngine import AvalonEngine
from discord.ext import commands
import discord.file
import random
import string
import os

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

class AvalonCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.lobbies = {}

    #Get parameters passed with a given command
    def getParams(self, ctx):
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        return ctx.message.content[len(prefix_used) + len(alias_used):].upper()
        
    #Send message to a given user via DM
    async def sendDM(self,user,message):
        channel = user.dm_channel()
        if not(user.dm_channel()):
            channel = await user.create_dm()
        await channel.send(message)

    #Returns a dict mapping player names to their player objects
    def genPlayerMap(self,players):
        playerMap = {}
        for player in players:
            playerMap[player.user.name.upper()]= player
        return playerMap

    #Returns a dict mapping usernames to their user objects
    def genNameToUserMap(self, users):
        nameToUserMap = {}
        for user in users:
            nameToUserMap[user.name.upper()] = user
        return nameToUserMap
    
    #Sends pdf with rules
    @commands.command()
    async def howToPlay(self, ctx):
        rules_file = os.path.join(THIS_FOLDER,'Avalon_Rules.pdf')
        with open(rules_file,'rb') as fp:
            await ctx.channel.send(file=discord.File(fp,'Avalon_Rules.pdf'))

    #Creates a new lobby with either a randomly generated lobby token or one passed by the lobby creator
    @commands.command(pass_context = True)
    async def startLobby(self,ctx):
        lobbyToken = self.getParams(ctx)
        if not(lobbyToken):
            lobbyToken = ''.join(random.choice(string.ascii_uppercase) for i in range(5))
        self.lobbies[lobbyToken] = {
            'players':[ctx.author],
            'specialCharacters':[],
            'locked': False
        }
        await ctx.channel.send("{} has started an avalon lobby, to join, type ava.join {} ".format(ctx.author, lobbyToken))

    #Prints information about a given lobby
    @commands.command(pass_context = True)
    async def getLobbyInfo(self, ctx):
        lobbyToken = self.getParams(ctx)
        if not(lobbyToken):
            await ctx.channel.send("No lobby given!")
        if not(lobbyToken in self.lobbies.keys()):
            await ctx.channel.send("{} is not a valid lobby".format(lobbyToken))
        else:
            await ctx.channel.send("Players in the lobby:")
            players = ''
            for player in self.lobbies[lobbyToken]['players']:
                players += (player.name)
                players += (" ")
            await ctx.channel.send("Participants: {}".format(players))
            await ctx.channel.send("Special Characters: {}".format(self.lobbies[lobbyToken]['specialCharacters']))
            if (self.lobbies[lobbyToken]['locked']):
                await ctx.channel.send("{} is locked".format(lobbyToken))
            else:
                await ctx.channel.send("{} is not locked".format(lobbyToken))

    #Prints a list of all current lobbies
    @commands.command(pass_context = True)
    async def showLobbies(self,ctx):
        lobbies = ''
        for lobby in self.lobbies.keys():
            lobbies += lobby
        if(lobbies):
            await ctx.channel.send(lobbies)
        else:
            await ctx.channel.send("No lobbies currently active")

    #Allows a player not currently in a given lobby to join said lobby
    @commands.command(pass_context = True)
    async def join(self, ctx):
        lobbyToken = self.getParams(ctx)
        if not(lobbyToken):
            await ctx.channel.send("No lobby given!")
        if not(lobbyToken in self.lobbies.keys()):
            await ctx.channel.send("{} is not a valid".format(lobbyToken))
            return
        if (self.lobbies[lobbyToken]['locked']):
            await ctx.channel.send("Cannot join lobby {}, lobby is locked".format(lobbyToken))
            return
        if not(ctx.author in self.lobbies[lobbyToken]['players']):
            self.lobbies[lobbyToken]['players'].append(ctx.author)
            await ctx.channel.send("{}, you have joined lobby {}".format(ctx.author.mention,lobbyToken))
        else:
            await ctx.channel.send("Cannot join {}, already in lobby!".format(lobbyToken))

    #Allows a player in a lobby to leave that lobby
    @commands.command(pass_context = True)
    async def leave(self, ctx):
        lobbyToken = self.getParams(ctx)
        if not(lobbyToken):
            await ctx.channel.send("No lobby given!")
        if not (lobbyToken in self.lobbies.keys()):
            await ctx.channel.send("{} is not a valid lobby".format(lobbyToken))
            return
        if (self.lobbies[lobbyToken]['locked']):
            await ctx.channel.send("Cannot leave lobby {}, lobby is locked".format(lobbyToken))
            return
        if (ctx.author in self.lobbies[lobbyToken]['players']):
            self.lobbies[lobbyToken]['players'].remove(ctx.author)
            await ctx.channel.send("{}, you have left lobby {}".format(ctx.author.name,lobbyToken))
        else:
            await ctx.channel.send("{}, you are not in lobby {}".format(ctx.author.name,lobbyToken))

    #Add special Characters to a lobby you're in
    @commands.command(pass_context = True)
    async def add(self, ctx):
        params = self.getParams(ctx).split()
        if(len(params) <= 1):
            await ctx.channel.send("Invalid add command")
            return
        lobbyToken = params[0]
        if not (lobbyToken in self.lobbies.keys()):
            await ctx.channel.send("{} is not a valid lobby".format(lobbyToken))
            return
        if not(ctx.author in self.lobbies[lobbyToken]['players']):
            await ctx.channel.send("{} cannot add characters, not currently in lobby {}".format(ctx.author.mention,lobbyToken))
            return    
        characters = params[1:]
        added = ""
        for character in characters:
            if (character == "MORDRED" and not(Mordred in self.lobbies[lobbyToken]['specialCharacters'])):
                self.lobbies[lobbyToken]['specialCharacters'].append(Mordred)
                added += " Mordred"
            elif (character == "MORGANA" and not(Morgana in self.lobbies[lobbyToken]['specialCharacters'])):
                self.lobbies[lobbyToken]['specialCharacters'].append(Morgana)
                added += " Morgana"
            elif (character == "OBERON" and not(Oberon in self.lobbies[lobbyToken]['specialCharacters'])):
                self.lobbies[lobbyToken]['specialCharacters'].append(Oberon)
                added += " Oberon"
            else:
                if (character == "PERCIVAL" and not(Percival in self.lobbies[lobbyToken]['specialCharacters'])):
                    self.lobbies[lobbyToken]['specialCharacters'].append(Percival)
                    added += " Percival"
        await ctx.channel.send("Added the following characters to lobby {}:{}".format(lobbyToken,added))

    #Remove special characters from a lobby you're in
    @commands.command(pass_context = True)
    async def remove(self, ctx):
        params = self.getParams(ctx).split()
        if(len(params) <= 1):
            await ctx.channel.send("Invalid remove command")
            return
        lobbyToken = params[0]
        if not(lobbyToken in self.lobbies.keys()):
            await ctx.channel.send("{} is not a valid lobby".format(lobbyToken))
            return
        if not(ctx.author in self.lobbies[lobbyToken]['players']):
            await ctx.channel.send("{} cannot remove characters, not currently in lobby {}".format(ctx.author.mention,lobbyToken))
            return    
        characters = params[1:]
        removed = ""
        for character in characters:
            if (character == "MORDRED" and (Mordred in self.lobbies[lobbyToken]['specialCharacters'])):
                self.lobbies[lobbyToken]['specialCharacters'].remove(Mordred)
                removed += " Mordred"
            elif (character == "MORGANA" and (Morgana in self.lobbies[lobbyToken]['specialCharacters'])):
                self.lobbies[lobbyToken]['specialCharacters'].remove(Morgana)
                removed += " Morgana"
            elif (character == "OBERON" and (Oberon in self.lobbies[lobbyToken]['specialCharacters'])):
                self.lobbies[lobbyToken]['specialCharacters'].remove(Oberon)
                removed += " Oberon"
            else:
                if (character == "PERCIVAL" and (Percival in self.lobbies[lobbyToken]['specialCharacters'])):
                    self.lobbies[lobbyToken]['specialCharacters'].remove(Percival)
                    removed += " Percival"
        await ctx.channel.send("Removed the following characters to lobby {}:{}".format(lobbyToken,removed))

    #Locks a lobby and begins a game of avalon with the players in the lobby
    @commands.command(pass_context = True)
    async def startGame(self, ctx):
        lobbyToken = self.getParams(ctx)
        if not(lobbyToken in self.lobbies.keys()):
            await ctx.channel.send("{} is not a valid lobby".format(lobbyToken))
            return
        if not(ctx.author in self.lobbies[lobbyToken]['players']):
            await ctx.channel.send("{} cannot start lobby {}, not currently joined".format(ctx.author.mention,lobbyToken))
            return
        playerCount = len(self.lobbies[lobbyToken]['players'])
        if (playerCount < 5):
            await ctx.channel.send("Cannot start lobby {}, not enough players".format(lobbyToken))
            return
        if (playerCount > 10):
            await ctx.channel.send("Cannot start lobby {}, too many players".format(lobbyToken))
        self.lobbies[lobbyToken]['locked'] = True
        self.runAvalonGame(ctx, self.lobbies[lobbyToken], lobbyToken)

    #runs a game of avalon for a givevn lobby
    async def runAvalonGame(self, ctx, lobby, lobbyToken):
        #Setting up game
        playerCount = len(lobby['players'])
        gameFormat = AvalonEngine.fetchGameSetup(playerCount)
        characters = AvalonEngine.genCharacterList(gameFormat['good'],gameFormat['evil'],lobby['specialCharacters'])
        questSizes = gameFormat['MissionTeamMembers']
        players = AvalonEngine.assignCharacters(lobby['players'],characters)
        playerMap = self.genPlayerMap(players)
        characterMap = AvalonEngine.genCharacterMap(players)
        leader = 0
        succesfulMissions = 0
        failedMissions = 0
        missionsLog = ['-','-','-','-','-']
        #Game now actually starts
        self.sendRoles(lobbyToken, players)
        self.reveal(lobbyToken, players, characterMap)
        for mission in range(5):
            await ctx.channel.send("Lobby {} Quest Team Sizes: Q1:{} Q2:{} Q3:{} Q4:{} Q5:{}".format(lobbyToken, questSizes[0],questSizes[1],questSizes[2],questSizes[3],questSizes[4]))
            await ctx.channel.send("Lobby {} Quest Results: Q1:{} Q2:{} Q3:{} Q4:{} Q5:{}".format(lobbyToken, missionsLog[0],missionsLog[1],missionsLog[2],missionsLog[3],missionsLog[4]))
            attempt = 1
            team = []
            while(not(bool(team))and attempt <= 5):
                team = self.proposeTeam(ctx,players,playerMap,leader,lobbyToken,questSizes[mission],mission+1,attempt)
                attempt += 1
            if (team):
                result = self.runMission(ctx,lobby, team,mission,playerMap)
            else:
                if (not(bool(team))and (attempt == 6)):
                    result = False
            if result:
                succesfulMissions += 1
                missionsLog[mission] = 'O'
            else:
                failedMissions += 1
                missionsLog[mission] = 'X'
            if(failedMissions == 2 or succesfulMissions == 3):
                break
        if (succesfulMissions == 3 and self.attemptAssassination(ctx,lobbyToken,playerMap,characterMap)):
            await ctx.channel.send("Lobby {}: Good Team Wins! Congratulations Good Guys!")
        else:
            await ctx.channel.send("Lobby {}: Bad Team Wins! Congratulations Bad Guys!")
        
    #Sends a message to all given players about what role they received
    async def sendRoles(self, lobbyToken, players):
        for player in players:
            await self.sendDM(player.user, "Lobby {}: You are: {}".format(lobbyToken, player.character.name))

    #Reveal characters to players based on the player's character
    async def reveal(self, lobbyToken, players, characterMap):
        for player in players:
            reveal = AvalonEngine.revealCharacters(player.character, characterMap)
            playerNames = []
            for player in reveal:
                playerNames.append(player.name)
            await self.sendDM(player,"Lobby {}: The following people have been revealed to you: {}".format(lobbyToken, playerNames))

    #Receives a team from the leader and proposes it to everyone, returns the proposed team if approved or an empty array if not approved
    async def proposeTeam(self, ctx, players, playerMap, leader, lobbyToken, teamSize, missionNum, attemptNum ):
        def check(m):
            return m.author == players[leader].user
        team = []
        await ctx.channel.send("Lobby {}: {} must propose {} people for mission {} attempt {}".format(lobbyToken,players[leader].user.name,teamSize,missionNum,attemptNum)).then()
        await ctx.channel.send("Please enter user names spaced")
        while(not(bool(team))):
            message = self.bot.waitFor('message',check=check).content.upper()
            proposedTeam = message.split()
            validTeam = True
            for member in proposedTeam:
                if not(member in playerMap):
                    validTeam = False
                playerMap.remove(member)
            if(validTeam  and len(proposedTeam) == teamSize):
                team = proposedTeam
        await ctx.channel.send("Lobby {}: {} has proposed the following team: {}".format(lobbyToken,players[leader].user.name, proposedTeam))
        for player in players:
            await self.sendDM(player.user, "Lobby {}: Do you approve of proposed team? please type y for yes, or n for no".format(lobbyToken))
        voteMap = {}
        voteMessage = ''
        while(players):
            #iterate through all players and check if we have a response from them
            for player in players:
                dm_channel = player.user.dm_channel()
                message = await dm_channel.history(limit=1).flatten()[0]
                if message.author == player.user:
                    messageContent = message.content.upper()
                    if messageContent == 'Y':
                        voteMap[player.user.name] = True
                        players.remove(player)
                        voteMessage += "{}: Approve ".format(player.user.name)
                    else:
                        if messageContent == 'N':
                            voteMap[player.user.name] == False
                            players.remove(player)
                            voteMessage += "{}: Unapprove ".format(player.user.name)
        isApproved = AvalonEngine.isTeamApproved(voteMap)
        isApprovedMessage = "Approved" if isApproved else "Unapproved"
        await ctx.channel.send("Lobby {}:Voting has completed, team is {}, votes were as follows:".format(lobbyToken,isApprovedMessage))
        await ctx.channel.send(voteMessage)
        if not(isApproved):
            proposedTeam = []
        return proposedTeam
    
    async def runMission(self, ctx, lobbyToken, team, missionNum, playerMap):
        teamUserList = []
        responses = []
        successMessage = []
        for member in team:
            if(member.character.isGood):
                self.sendDM(member.user,"Lobby {}: You are good. When you are ready, type p to pass the mission".format(lobbyToken))
            else:
                self.sendDM(member.user,"Lobby {}: You are bad. Please type p to pass the mission or f to fail it".format(lobbyToken))
            teamUserList.append(playerMap[member])
        while(team):
            for member in teamUserList:
                dm_channel = member.user.dm_channel()
                message = await dm_channel.history(limit=1).flatten()[0]
                if message.author == member.user:
                    messageContent = message.content.upper()
                    if messageContent == 'P':
                        True
                        team.remove(member.user.name)
                        successMessage.append("Pass")
                    else:
                        if not(member.character.isGood) and messageContent == 'F':
                            responses.append(False)
                            team.remove(member.user.name)
                            successMessage.append("Fail")
        random.shuffle(successMessage)
        if(missionNum == 2):
            succeeded = AvalonEngine.doesQuestThreePass(responses)
        else:
            succeeded = AvalonEngine.doesQuestPass(responses)
        if(succeeded):
            await ctx.channel.message("Lobby {}: Mission {} has passed!".format(lobbyToken,missionNum+1))
        else:
            await ctx.channel.message("Lobby {}: Mission {} has failed!".format(lobbyToken,missionNum+1))
        await ctx.channel.message("These were the responses : {}".format(successMessage))
        return succeeded
         
    async def attemptAssassination(self, ctx, lobbyToken, playerMap, characterMap):
        assassin = characterMap["Assassin"][0]
        target = ''
        def check(m):
            return m.author == assassin.user
        await ctx.send("Lobby {}: {} can now try to assassinate merlin, please enter the name of the user you want to assassinate".format(lobbyToken,assassin.user.name))
        while not(target):
            message = self.bot.waitFor('message',check=check).content.upper()
            if (message in playerMap):
                target = playerMap[message]
        if (playerMap[target].character == Merlin):
            return True
        return False

def setup(bot):
    bot.add_cog(AvalonCog(bot))