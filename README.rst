discord-storage
==========
Proof of concept of storing files in Discord

Idea from video by `Dev Detour <https://www.youtube.com/watch?v=c_arQ-6ElYI>`_

Discord very specifically says in it's ToS that they can ban 
you or delete your server for whatever reason without any 
chance of getting stuff back. 

It has happened before and entire communities are lost.

**DO NOT store anything critical with this!**


Basic Setup:
-------------

1. Go to the discord developer portal and create an application

2. Copy the discord bot token and save that to the work env

3. Create a new server with a channel for your files to be stored in

4. Once the bot is running use !setup to set the dump channel

5. Use !addfile to add files and !dwnfile to download them



**Limited testing**
-------------
Has only been used with a few small files nothing over a gb in size


**Links**
-------------
- `discord.py Documentation <https://discordpy.readthedocs.io/en/latest/index.html>`_

- `Discord API <https://discord.gg/discord-api>`_
