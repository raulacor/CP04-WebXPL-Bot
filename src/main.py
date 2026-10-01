import os
import io
import discord
import subprocess
import requests

from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()

bot = commands.Bot(command_prefix='!', intents=intents) #Calling the bot.


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot loaded, {bot.user.name}")

@bot.tree.command(name="help", description="Ask black hands for help.")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Commands Available", color=discord.Color.dark_blue())
    embed.add_field(name="/dependencies", value="Installs all required dependencies", inline=False)
    embed.add_field(name="/nmap <host>", value="Port/service scan", inline=False)
    embed.add_field(name="/gau <host>", value="Gather endpoints passively using GetAllURL", inline=False)
    embed.add_field(name="/ipinfo <host>", value="Gather info on target ip", inline=False)
    await interaction.response.send_message(embed=embed)


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

@bot.tree.command(name="ipinfo", description="Gather info on target ip")
async def ipinfo(interaction: discord.Interaction, target:str):
    await interaction.response.defer(ephemeral=True)
    try:
        ipinfo_response = requests.get(f"https://ipinfo.io/{target}/json")
        if ipinfo_response.ok:
            ipinfo_result = ipinfo_response.json()
            await interaction.followup.send(
f"""
Scanned IP: {ipinfo_result.get('ip')}
Hostname: {ipinfo_result.get('hostname')}
City: {ipinfo_result.get('city')}
Region: {ipinfo_result.get('region')}
Country: {ipinfo_result.get('country')}
Location: {ipinfo_result.get('loc')}
Org: {ipinfo_result.get('org')}
Postal: {ipinfo_result.get('postal')}
Timezon: {ipinfo_result.get('timezone')}
"""
        )
        else:
            await interaction.followup.send(f"Request failed with status code: {ipinfo_response.status_code}")

    except requests.exceptions.RequestException:
        await interaction.followup.send("Error: Couldn't reach server")

@bot.tree.command(name="crt", description="Gather certificate info on a target domain")
async def crt(interaction: discord.Interaction, target:str):
    await interaction.response.defer(ephemeral=True)
    try:
        crt_response = requests.get(f"https://crt.sh/?q={target}&output=json")
        if crt_response.ok:
            crt_result = crt_response.json()
            subdomains = set()
            
            for cert in crt_result:
                subdomains.update(cert.get("name_value").split("\n"))


            crt_text = "\n".join(subdomains)
            crt_buffer = io.BytesIO(crt_text.encode('utf-8'))
            crt_file = discord.File(fp=crt_buffer, filename="crt.txt")

            await interaction.followup.send(file=crt_file)

        else:
            await interaction.followup.send(f"Request failed with status code: {crt_response.status_code}")

    except requests.exceptions.RequestException:
        await interaction.followup.send("Error: Couldn't reach server")

bot.run(token)