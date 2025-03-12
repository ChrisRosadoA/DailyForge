import discord
from discord.ext import commands
from datetime import datetime
import json
import bot_classes.taskChecks as taskChecks
from bot_classes.dataManager import data

# FUNCTION: Load the bot token from config.json
with open("config.json", "r") as f:
    config = json.load(f)
    bot_token = config["token"]

# DISCORD BOT:  Setup the bot
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

# EVENT: on_ready - Runs when the bot is online
@bot.event
async def on_ready():
    """Sends a welcome message when the bot is online."""
    print("Obtaining bot information...")
    print(f"Logged in as {bot.user}") #Gives the entire user object info (including ID, discriminator, etc.)
    
    channel_id = config.get("channel_id") # Get the channel ID from config.json


#MOD So that if no channel ID is assigned, it lets the user know to go through first time setup 

    if channel_id:
        channel = bot.get_channel(int(channel_id))
       
        if channel:
            await channel.send("✅ Welcome! The Daily Forge is now ready for use!")

        else:
            print(f"⚠️ Could not find the channel with ID {channel_id}.")
    else:
       print("⚠️ No channel ID found. Use !set_channel to set one.")


# COMMAND: Set Channel where the bot will send messages
@bot.command()
async def set_channel(ctx):
    """Sets the channel where the bot will send messages."""
    channel_id = str(ctx.channel.id)  # Use the current channel's ID
    with open("config.json", "r") as f:
        config = json.load(f)

    config["channel_id"] = channel_id

    # Save the updated config
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    await ctx.send(f"✅ Channel set to {ctx.channel.name}!")

from datetime import datetime, timezone

# COMMAND: Set goals for the user
@bot.command()
async def checkin(ctx): 
    """Sends an interactive check-in message with checkmark buttons."""
    user_id = str(ctx.author.id)
    
    # Use timezone-aware UTC time
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if user_id in data["users"]:
        end_date = data["users"][user_id].get("end_date", today)

        if today > end_date:
            await ctx.send("⏳ Your goal tracking period has ended! Set new goals using `!set_goals`.") 
            return

        goals = data["users"][user_id]["goals"]
        if not goals:
            await ctx.send("You don't have any tasks set!")
            return

        view = taskChecks.TaskCheckinView(user_id, goals)
        await ctx.send("📝 Click a button to mark your tasks as completed!", view=view)
    else:
        await ctx.send("You haven't set any goals yet! Use `!set_goals` first.")

# Run the bot with the token from config.json
bot.run(bot_token)

