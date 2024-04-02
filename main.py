import discord
import io
from discord import app_commands
import kiepski_random_frame
import json
import sqlite3

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
connection = None

def table_exists(cursor,table_name):
    cursor.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?''', (table_name,))
    return cursor.fetchone()[0] == 1

async def setup_hook():
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)
    global connection 
    connection = get_db_connection(config["guild_id"])
    cursor = connection.cursor()
    if table_exists(cursor, "episode") == False and table_exists(cursor,"frame") == False:
        print("seeding db")
        kiepski_random_frame.seed_db(config["episodes_path"], cursor)
        connection.commit()
        connection.close()
        print("seeded")

def get_db_connection(guildId):
    con = sqlite3.connect(f"{guildId}.db")
    return con

@client.event
async def on_ready():
    print("On ready")
    await setup_hook()

@tree.command(name="kiepskiframe")
async def random_kiepski(interaction):
    connection = get_db_connection(config["guild_id"])
    image, episode, _ = kiepski_random_frame.get_random_frame(connection.cursor()) 
    connection.commit()
    connection.close()
    text = f"{episode[4]}. {episode[1]}"
    await interaction.response.send_message(text, file=discord.File(io.BytesIO(image.tobytes()), 'image.png'))

client.run(config["bot_token"])
