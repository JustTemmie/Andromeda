import discord
from discord.ext import commands
class VoiceChannelMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_to_monitor = 801834123798904893
        self.target_user = 725539745572323409 
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.user_to_monitor and after.channel is not None:
            for channel_member in after.channel.members:
                if channel_member.id == self.target_user:
                    await member.move_to(None)
                    return
        
        if member.id == self.target_user and after.channel is not None:
            for channel_member in after.channel.members:
                if channel_member.id == self.user_to_monitor:
                    await after.channel.guild.get_member(self.user_to_monitor).move_to(None)
                    return
    
async def setup(bot):
    await bot.add_cog(VoiceChannelMonitor(bot))