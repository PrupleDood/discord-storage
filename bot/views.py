
from typing import Any
import traceback
import asyncio
import os

import discord
from discord import ui
from discord.interactions import Interaction
from discord.ui.item import Item

from bot.file_cmds import upload_file, download_file
from bot.db_files import db


async def upload_callback(interaction: Interaction, file_path: str, channel: discord.TextChannel):
    upload_task = asyncio.create_task(
        coro = upload_file(file_path, channel),
        name = f"{file_path}_upload"
    )

    await interaction.response.defer()

    webhook = interaction.followup

    await webhook.send(content = "File Is Being Uploading!", ephemeral = True)

    async def task_callback():
        # Takes the filename from the path
        await webhook.send(content = f"{os.path.split(file_path)[1]} Finished Uploading", ephemeral = True)

    # Used to make callback function asynchronus 
    upload_task.add_done_callback(lambda _ : asyncio.create_task(task_callback()))


async def download_callback(interaction: Interaction, parent_file: str):
    download_task = asyncio.create_task(
        download_file(parent_file, interaction.guild)
    )

    await interaction.response.defer()

    webhook = interaction.followup

    await webhook.send(content = f"{parent_file} Is Being Downloaded!", ephemeral = True)

    async def task_callback():
        await webhook.send(content = f"{parent_file} Finished Downloading", ephemeral = True)

    # Used to make callback function asynchronus 
    download_task.add_done_callback(lambda _ : asyncio.create_task(task_callback()))


class ChannelSelect(ui.ChannelSelect):

    def __init__(self):
        channeltypes = [discord.ChannelType.text]

        super().__init__(
            channel_types = channeltypes,
            placeholder = "Select a channel..."
        )

    async def callback(self, interaction: Interaction) -> Any:
        await interaction.response.edit_message(content = "")

    async def on_error(interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class FileSelect(ui.Select):

    def __init__(self, upload:bool = False, folder_path:str = None, files:list = None):
        super().__init__()
        
        if upload:
            for i, file in enumerate(files):
                self.append_option(discord.SelectOption(
                    label = file,
                    value = os.path.join(folder_path, file),
                    default = False if i > 0 else True 
                ))

        else:
            parent_files = db.get_parent_files()

            for i, parent_file in enumerate(parent_files):
                self.append_option(discord.SelectOption(
                    label = parent_file,
                    value = parent_file,
                    default = False if i > 0 else True
                ))


    async def callback(self, interaction: Interaction) -> Any:
        # Changes default option so it appears as the selected option
        default_options = [option for option in self.options if option.default == True or option.value in self.values]

        for option in default_options:
            if len(default_options) != 1:
                option.default = not option.default
            
            elif len(default_options) == 1:
                option.default = True

        # Used to avoid a failed interaction
        await interaction.response.edit_message(
            view = self.view
        )


    async def on_error(interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class SubmitButton(ui.Button):
    def __init__(self, callback_func):
        self.callback_func = callback_func

        super().__init__(label = "Submit")


    async def callback(self, interaction: Interaction) -> Any:
        await self.callback_func(self, interaction)


    async def on_error(interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class CancelButton(ui.Button):

    def __init__(self):
        super().__init__(label = "Cancel")


    async def callback(self, interaction : Interaction):
        await interaction.message.delete()
        await interaction.response.send_message("Canceled", ephemeral = True)


    async def on_error(interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class DumpChannel(ui.View):

    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)

        self.add_item(ChannelSelect())
        self.add_item(CancelButton())
        self.add_item(SubmitButton(callback_func = self.callback))

    @staticmethod
    async def callback(button: ui.Button, interaction: Interaction):
        dump_channel : discord.TextChannel = [child.values[0] for child in button.view.children if isinstance(child, ChannelSelect)][0]

        os.environ["GUILDID"] = str(dump_channel.guild.id)
        os.environ["CHANNELID"] = str(dump_channel.id)

        with open(f"{os.getcwd()}/bot/data", "w") as file:
            file.write(f"{dump_channel.guild.id}\n{dump_channel.id}")

        await interaction.response.send_message(f"Channel updated to {dump_channel.name}",ephemeral = True)


    async def on_error(interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class AddFile(ui.View):
    
    dump_channel = None
    file_path = None

    def __init__(self, *, timeout: float | None = 180, channel:discord.TextChannel = None):
        super().__init__(timeout=timeout)

        AddFile.dump_channel = channel

        folder_name = "uploads"
        folder_path = os.path.join(os.getcwd(), folder_name)

        files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

        if len(files) == 0:
            raise ValueError(f"No Files in {folder_name}") 

        elif len(files) > 1:
            self.add_item(FileSelect(
                upload = True,
                folder_path = folder_path,
                files = files
            ))

        else:
            AddFile.file_path = files[0]

        self.add_item(CancelButton())
        self.add_item(SubmitButton(callback_func = self.callback))

    @staticmethod
    async def callback(button: ui.Button, interaction: Interaction):
        select = [child for child in button.view.children if isinstance(child, FileSelect)][0]

        if len(select.values) == 0:
            file_path = [option.value for option in select.options if option.default == True][0]
        
        else:
            file_path = select.values[0] 

        await upload_callback(interaction, file_path, AddFile.dump_channel)


    async def on_error(self, interaction: Interaction, error: Exception, item: Item[Any]) -> None:
        return await interaction.response.send_message(f"{str(error)} from {item}")


    def _is_confirm(self):
        return len([child for child in self.children if isinstance(child, FileSelect)]) > 1

    # TODO figure out why option list doesnt keep option


class DownloadFile(ui.View):

    parent_file = None

    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)

        self.add_item(FileSelect(
            upload = False
        ))

        self.add_item(CancelButton())
        self.add_item(SubmitButton(callback_func = self.callback))

    @staticmethod
    async def callback(button: ui.Button, interaction: Interaction):
        parent_file = [child.values[0] for child in button.view.children if isinstance(child, FileSelect)][0]

        await download_callback(interaction, parent_file)
