#!/usr/bin/env python3

import os
import discord

from discord.ext import commands
from bot.commands import def_commands


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        # intents = discord.Intents.default()
        # intents.message_content = True
        
        super().__init__(command_prefix = '!', intents = intents)
        
    async def on_ready(self):
        print(f'We have logged in as {self.user} (ID : {self.user.id})')
    
    async def setup_hook(self):

        def_commands(self)

        await self.tree.sync()


bot = Bot()

TOKEN = os.environ["TOKEN"]

with open(f"{os.getcwd()}/bot/data", "r") as file:
    data = file.read().split("\n")

    try:
        ids = [int(line) for line in data]

        os.environ["GUILDID"] = str(ids[0])
        os.environ["CHANNELID"] = str(ids[1])

    except ValueError:
        print(f"WARNING : DUMPCHANNEL NOT SETUP USE !setup")


def run_bot():
    bot.run(TOKEN)