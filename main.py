import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True

testing = False

client = commands.Bot(command_prefix = "bro!", case_insensitive = False, intents=intents)

client.remove_command('help')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run('OTEzNDAyMTg3NjY3ODY5NzA2.YZ9-Ew.3pPy0POwazrSlMex7zw8TcczVwI')