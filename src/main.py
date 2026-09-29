import os
import io
import discord
import subprocess

from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents) #Calling the bot.


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot loaded, {bot.user.name}")

@bot.tree.command(name="nmap", description="Run: nmap -sV")
async def nmap(interaction: discord.Interaction, msg:str):
    await interaction.response.defer(ephemeral=True)
    try:
        nmap_result = subprocess.run(["nmap", "-sV", "--version-light", "--script=banner", msg], capture_output=True, text=True)
        if nmap_result.returncode != 0:
            await interaction.followup.send("Error: target unavailable")
        else:
            nmap_buffer = io.BytesIO(nmap_result.stdout.encode('utf-8'))
            nmap_file = discord.File(fp=nmap_buffer, filename="nmap.txt")
            await interaction.followup.send(file=nmap_file)

    except FileNotFoundError:
        await interaction.followup.send("Error: nmap unavailable")


bot.run(token)