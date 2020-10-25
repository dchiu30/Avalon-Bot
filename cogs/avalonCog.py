from avalon.avalonCharacters import Assassin, Merlin, Minion, Mordred, Morgana, Oberon, Percival, Servant
from avalon.avalonEngine import AvalonEngine
from discord.ext import commands
import random
import string

class AvalonCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.lobbies = {}

    #Get parameters passed with a given command
    def getParams(self, ctx):
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        return ctx.message.content[len(prefix_used) + len(alias_used):].lower()
        
    #Send message to a given user via DM
    async def sendDM(self,user,message):
        channel = user.dm_channel()
        if~(user.dm_channel()):
            channel = await user.create_dm()
        await channel.send(message)

    def genPlayerMap(self,players):
        playerMap = {}
        for player in players:
            playerMap[player.user.name]= player
        return playerMap

    def genNameToUserMap(self, users):
        nameToUserMap = {}
        for user in users:
            nameToUserMap[user.name] = user
        return nameToUserMap

    #Creates a new lobby with either a randomly generated token or one passed by the lobby creator
    @commands.command(pass_context = True)
    def startLobby(self,ctx):
        lobbyToken = self.getParams(ctx)
        if ~(lobbyToken):
            lobbyToken = ''.join(random.choice(string.ascii_uppercase) for i in range(5))
        self.lobbies[lobbyToken] = {
            'players':[ctx.author],
            'specialCharacters':[],
            'locked': False
        }
        ctx.channel.send("{} has started an avalon lobby, to join, type ava.join {} ".format(ctx.author, lobbyToken))

    #Allows a player not currently in a given lobby to join said lobby
    @commands.command(pass_context = True)
    def join(self, ctx):
        token = self.getParams(ctx)
        if token in self.lobbies:
            if(~self.lobbies[token].locked):
                if ~(ctx.author in self.lobbies[token]['players']):
                    self.lobbies[token]['players'].append(ctx.author)
                    ctx.channel.send("{}, you have joined lobby {}".format(ctx.author.mention,token))
            else:
                ctx.channel.send("Cannot join lobby {}, lobby is locked".format(token))
        else:
            ctx.channel.send("{} is not a valid token".format(token))

    #Allows a player in a lobby to leave that lobby
    @commands.command(pass_context = True)
    def leave(self, ctx):
        token = self.getParams(ctx)
        if token in self.lobbies:
            if(~self.lobbies[token].locked):
                if (ctx.author in self.lobbies[token]['players']):
                    self.lobbies[token]['players'].remove(ctx.author)
                    ctx.channel.send("{}, you have left lobby {}".format(ctx.author.mention,token))
            else:
                ctx.channel.send("Cannot leave lobby {}, lobby is locked".format(token))
        else:
            ctx.channel.send("{} is not a valid token".format(token))

    #Add special Characters to a lobby you're in
    @commands.command(pass_context = True)
    def add(self, ctx):
        params = self.getParams(ctx).split()
        if(len(params) <= 1):
            ctx.channel.send("Invalid add command")
            return
        token = params[0]
        if ~(ctx.author in self.lobbies[token]['players']):
            ctx.channel.send("{} cannot add characters, not currently in lobby {}".format(ctx.author.mention,token))
            return    
        characters = params[1:]
        added = ""
        for character in characters:
            if (character == "mordred" and not(Mordred in self.lobbies[token]['specialCharacters'])):
                self.lobbies[token]['specialCharacters'].append(Mordred)
                added.join(" Mordred")
            elif (character == "morgana" and not(Morgana in self.lobbies[token]['specialCharacters'])):
                self.lobbies[token]['specialCharacters'].append(Morgana)
                added.join(" Morgana")
            elif (character == "oberon" and not(Oberon in self.lobbies[token]['specialCharacters'])):
                self.lobbies[token]['specialCharacters'].append(Oberon)
                added.join(" Oberon")
            else:
                if (character == "percival" and not(Percival in self.lobbies[token]['specialCharacters'])):
                    self.lobbies[token]['specialCharacters'].append(Percival)
                    added.join(" Percival")
        ctx.channel.send("Added the following characters to lobby {}:{}".format(token,added))

    #Remove special characters from a lobby you're in
    @commands.command(pass_context = True)
    def remove(self, ctx):
        params = self.getParams(ctx).split()
        if(len(params) <= 1):
            ctx.channel.send("Invalid remove command")
            return
        token = params[0]
        if ~(ctx.author in self.lobbies[token]['players']):
            ctx.channel.send("{} cannot remove characters, not currently in lobby {}".format(ctx.author.mention,token))
            return    
        characters = params[1:]
        removed = ""
        for character in characters:
            if (character == "mordred" and (Mordred in self.lobbies[token]['specialCharacters'])):
                self.lobbies[token]['specialCharacters'].remove(Mordred)
                removed.join(" Mordred")
            elif (character == "morgana" and (Morgana in self.lobbies[token]['specialCharacters'])):
                self.lobbies[token]['specialCharacters'].remove(Morgana)
                removed.join(" Morgana")
            elif (character == "oberon" and (Oberon in self.lobbies[token]['specialCharacters'])):
                self.lobbies[token]['specialCharacters'].remove(Oberon)
                removed.join(" Oberon")
            else:
                if (character == "percival" and (Percival in self.lobbies[token]['specialCharacters'])):
                    self.lobbies[token]['specialCharacters'].remove(Percival)
                    removed.join(" Percival")
        ctx.channel.send("Removed the following characters to lobby {}:{}".format(token,removed))

    #Locks a lobby and begins a game of avalon with the players in the lobby
    @commands.command(pass_context = True)
    def startGame(self, ctx):
        token = self.getParams(ctx)
        if ~(token in self.lobbies):
            ctx.channel.send("{} is not a valid token".format(token))
            return
        if ~(ctx.author in self.lobbies[token]['players']):
            ctx.channel.send("{} cannot start lobby {}, not currently joined".format(ctx.author.mention,token))
            return
        playerCount = len(self.lobbies[token]['players'])
        if (playerCount < 5):
            ctx.channel.send("Cannot start lobby {}, not enough players".format(token))
            return
        if (playerCount > 10):
            ctx.channel.send("Cannot start lobby {}, too many players".format(token))
        self.lobbies[token]['locked'] = True
        self.runAvalonGame(ctx, self.lobbies[token], token)

    #runs a game of avalon for a givevn lobby
    def runAvalonGame(self, ctx, lobby, lobbyToken):
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
            ctx.channel.send("Lobby {} Quest Team Sizes: Q1:{} Q2:{} Q3:{} Q4:{} Q5:{}".format(lobbyToken, questSizes[0],questSizes[1],questSizes[2],questSizes[3],questSizes[4]))
            ctx.channel.send("Lobby {} Quest Results: Q1:{} Q2:{} Q3:{} Q4:{} Q5:{}".format(lobbyToken, missionsLog[0],missionsLog[1],missionsLog[2],missionsLog[3],missionsLog[4]))
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
            ctx.channel.send("Lobby {}: Good Team Wins! Congratulations Good Guys!")
        else:
            ctx.channel.send("Lobby {}: Bad Team Wins! Congratulations Bad Guys!")
        
    #Sends a message to all given players about what role they received
    def sendRoles(self, token, players):
        for player in players:
            await self.sendDM(player.user, "Lobby {}: You are: {}".format(token, player.character.name))

    #Reveal characters to players based on the player's character
    def reveal(self, token, players, characterMap):
        for player in players:
            reveal = AvalonEngine.revealCharacters(player.character, characterMap)
            playerNames = []
            for player in reveal:
                playerNames.append(player.name)
            await self.sendDM(player,"Lobby {}: The following people have been revelaed to you: {}".format(token, playerNames))

    #Receives a team from the leader and proposes it to everyone, returns the proposed team if approved or an empty array if not approved
    def proposeTeam(self, ctx, players, playerMap, leader, token, teamSize, missionNum, attemptNum ):
        def check(m):
            return m.author == players[leader].user
        team = []
        await ctx.channel.send("Lobby {}: {} must propose {} people for mission {} attempt {}".format(token,players[leader].user.name,teamSize,missionNum,attemptNum)).then()
        await ctx.channel.send("Please enter user names spaced")
        while(not(bool(team))):
            message = self.bot.waitFor('message',check=check)
            proposedTeam = message.split()
            validTeam = True
            for member in proposedTeam:
                if not(member in playerMap):
                    validTeam = False
                playerMap.remove(member)
            if(validTeam  and len(proposedTeam) ==teamSize):
                team = proposedTeam
        await ctx.channel.send("Lobby {}: {} has proposed the following team: {}".format(token,players[leader].user.name, proposedTeam))
        for player in players:
            self.sendDM(player.user, "Lobby {}: Do you approve of proposed team? please type y for yes, or n for no".format(token))
        voteMap = {}
        voteMessage = ''
        while(players):
            #iterate through all players and check if we have a response from them
            for player in players:
                dm_channel = player.user.dm_channel()
                message = dm_channel.history(limit=1).flatten()[0]
                if message.author == player.user:
                    messageContent = message.content.lower()
                    if messageContent == 'y':
                        voteMap[player.user.name] = True
                        players.remove(player)
                        voteMessage.join("{}: Approve ".format(player.user.name))
                    else:
                        if messageContent == 'n':
                            voteMap[player.user.name] == False
                            players.remove(player)
                            voteMessage.join("{}: Unapprove ".format(player.user.name))
        isApproved = AvalonEngine.isTeamApproved(voteMap)
        isApprovedMessage = "Approved" if isApproved else "Unapproved"
        ctx.channel.send("Lobby {}:Voting has completed, team is {}, votes were as follows:".format(token,isApprovedMessage))
        ctx.send(voteMessage)
        if not(isApproved):
            proposedTeam = []
        return proposedTeam
    
    def runMission(self, ctx, token, team, missionNum, playerMap):
        teamUserList = []
        responses = []
        successMessage = ''
        for member in team:
            if(member.character.isGood):
                self.sendDM(member.user,"Lobby {}: You are good. When you are ready, type p to pass the mission".format(token))
            else:
                self.sendDM(member.user,"Lobby {}: You are bad. Please type p to pass the mission or f to fail it".format(token))
            teamUserList.append(playerMap[member])
        while(team):
            for member in teamUserList:
                dm_channel = member.user.dm_channel()
                message = dm_channel.history(limit=1).flatten()[0]
                if message.author == member.user:
                    messageContent = message.content.lower()
                    if messageContent == 'p':
                        True
                        team.remove(member.user.name)
                        successMessage.join("Pass ")
                    else:
                        if not(member.character.isGood) and messageContent == 'f':
                            responses.append(False)
                            team.remove(member.user.name)
                            successMessage.join("Fail ")
        random.shuffle(successMessage)
        if(missionNum == 2):
            succeeded = AvalonEngine.doesQuestThreePass(responses)
        else:
            succeeded = AvalonEngine.doesQuestPass(responses)
        if(succeeded):
            ctx.channel.message("Lobby {}: Mission {} has passed!".format(token,missionNum+1))
        else:
            ctx.channel.message("Lobby {}: Mission {} has failed!".format(token,missionNum+1))
        ctx.channel.message("These were the responses : {}".format(successMessage))
        return succeeded
         
    def attemptAssassination(self, ctx, token, playerMap, characterMap):
        assassin = characterMap["Assassin"][0]
        target = ''
        def check(m):
            return m.author == assassin.user
        ctx.send("Lobby {}: {} can now try to assassinate merlin, please enter the name of the user you want to assassinate".format(token,assassin.user.name))
        while not(target):
            message = self.bot.waitFor('message',check=check)
            if (message in playerMap):
                target = playerMap[message]
        if (playerMap[target].character == Merlin):
            return True
        return False

def setup(bot):
    bot.add_cog(AvalonCog(bot))