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

@bot.tree.command(name="dependencies", description="Install all required dependencies to run the program.")
async def dependencies(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        dependencies_result = subprocess.run("sudo -n apt update && sudo -n apt install -y nmap golang && go install github.com/lc/gau/v2/cmd/gau@latest",shell=True)
        if dependencies_result.returncode != 0:
            await interaction.followup.send("[ERROR]: Error installing dependencies.")
        else:
            await interaction.followup.send("[ALERT]: dependencies intalled.")

    except FileNotFoundError:
        await interaction.followup.send("Error: Make sure the bot is running on a linux distro.")      

@bot.tree.command(name="nmap", description="Run: nmap -sV")
async def nmap(interaction: discord.Interaction, target:str):
    await interaction.response.defer(ephemeral=True)
    try:
        nmap_result = subprocess.run(["nmap", "-sV", "--version-light", "--script=banner", target], capture_output=True, text=True)
        if nmap_result.returncode != 0:
            await interaction.followup.send("Error: target unavailable")
        else:
            nmap_buffer = io.BytesIO(nmap_result.stdout.encode('utf-8'))
            nmap_file = discord.File(fp=nmap_buffer, filename="nmap.txt")
            await interaction.followup.send(file=nmap_file)

    except FileNotFoundError:
        await interaction.followup.send("Error: nmap unavailable")

@bot.tree.command(name="gau", description="Gather endpoints passively using GetAllURL")
async def gau(interaction: discord.Interaction, domain:str):
    await interaction.response.defer(ephemeral=True)
    try:
        gau_result = subprocess.run(["gau", domain], capture_output=True, text=True)
        if gau_result.returncode != 0:
            await interaction.followup.send("Error: target unavailable")
        else:
            gau_buffer = io.BytesIO(gau_result.stdout.encode('utf-8'))
            gau_file = discord.File(fp=gau_buffer, filename="gau.txt")
            await interaction.followup.send(file=gau_file)

    except FileNotFoundError:
        await interaction.followup.send("Error: GetAllURL unavailable")


bot.run(token)