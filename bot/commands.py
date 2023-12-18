
import traceback
import discord
import os

from discord.ext import commands
from bot.views import DumpChannel, AddFile, DownloadFile


def def_commands(bot : commands.Bot):

    async def get_dump_channel():
        try:
            guild = await bot.fetch_guild(os.environ["GUILDID"])

            dump_channel = await guild.fetch_channel(os.environ["CHANNELID"])
        
        except discord.DiscordException as error:
            # Make sure we know what the error actually is
            traceback.print_exception(type(error), error, error.__traceback__)

        return dump_channel


    @bot.command()
    async def terminate(ctx: commands.Context): 
        '''Terminates the process'''
        await ctx.send('Terminating program...')
        await ctx.channel.purge(limit=2)
        
        await bot.close()
    
        exit(0)


    @bot.command()
    async def setup(ctx: commands.Context):
        await ctx.channel.send(view = DumpChannel())


    @bot.command()
    async def addfile(ctx: commands.Context):
        dump_channel = await get_dump_channel()

        view = AddFile(channel = dump_channel)
        embed = None

        if view._is_confirm():
            embed = discord.Embed(
                title = "Confirm File", 
                description = os.path.split(view.file_path)[0], 
                colour = discord.Color.blue()
            )

        await ctx.channel.send(
            embed = embed, 
            view = view
        )


    @bot.command()
    async def dwnfile(ctx: commands.Context):
        await ctx.channel.send(view = DownloadFile())


    @bot.command()
    async def test(ctx: commands.Context):
        pass

