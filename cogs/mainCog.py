from discord.ext import commands
from .avalonCog import AvalonCog

class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self.bot))
        self.bot.add_cog(AvalonCog(self.bot))
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith('$foo'):
            await message.channel.send('bar')

def setup(bot):
    bot.add_cog(MainCog(bot))