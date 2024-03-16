import discord
import io
from discord.ext import commands
from discord import app_commands
import kiepski_random_frame
import json

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

config = load_config("config.json")

MY_GUILD = discord.Object(id=config["guild_id"])

intents = discord.Intents.default()
client = discord.Client(intents=intents)
intents.message_content = True
tree = app_commands.CommandTree(client)

async def setup_hook():
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)

@client.event
async def on_ready():
    print("On ready")
    await setup_hook()

@tree.command(name="kiepskiframe")
async def random_kiepski(interaction):
    image, text = kiepski_random_frame.kiepski_random_frame(config["episodes_path"]) 
    await interaction.response.send_message(text, file=discord.File(io.BytesIO(image.tobytes()), 'image.png'))

client.run(config["bot_token"])
