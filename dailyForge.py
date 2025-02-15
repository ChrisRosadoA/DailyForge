import discord
from discord.ext import commands
from datetime import datetime
import random
import json

# Load the bot token from config.json
with open("config.json", "r") as f:
    config = json.load(f)
    bot_token = config["token"]

# Load user data from data.json
def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}}

# Save user data to data.json
def save_data():
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

# Initialize user data
data = load_data()

class TaskCheckinView(discord.ui.View):
    def __init__(self, user_id, tasks):
        super().__init__(timeout=86400)  # Buttons stay active for 24 hours
        self.user_id = user_id
        self.tasks = tasks
        self.completed_tasks = set()

        for i, task in enumerate(tasks):
            self.add_item(TaskButton(label=task, custom_id=f"task_{i}", view=self))

    async def task_completed(self, interaction: discord.Interaction, task_id):
        """Handles task completion when a user clicks a button."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This check-in isn't for you!", ephemeral=True)
            return

        self.completed_tasks.add(task_id)
        await interaction.response.send_message(f"✅ Task **{self.tasks[task_id]}** completed!", ephemeral=True)

        if len(self.completed_tasks) == len(self.tasks):  # All tasks completed
            await self.reward_xp(interaction)

    async def reward_xp(self, interaction: discord.Interaction):
        """Rewards XP after all tasks are checked off."""
        user_id = str(interaction.user.id)
        xp_gain = random.randint(5, 15)

        data["users"][user_id]["xp"] += xp_gain
        level = data["users"][user_id]["level"]

        if data["users"][user_id]["xp"] >= level * 50:
            data["users"][user_id]["level"] += 1
            level_up_msg = f"🎉 {interaction.user.mention} leveled up to {data['users'][user_id]['level']}! 🎉"
        else:
            level_up_msg = ""

        save_data()
        await interaction.message.edit(content=f"✅ All tasks completed! You earned **{xp_gain} XP**.\n{level_up_msg}", view=None)

class TaskButton(discord.ui.Button):
    def __init__(self, label, custom_id, view):
        super().__init__(style=discord.ButtonStyle.success, label=label, custom_id=custom_id)
        self.view = view

    async def callback(self, interaction: discord.Interaction):
        """Handles button clicks."""
        task_id = int(self.custom_id.split("_")[1])
        await self.view.task_completed(interaction, task_id)
        self.disabled = True  # Disable button after clicking
        await interaction.message.edit(view=self.view)

# Setup the bot
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix="!", intents=intents)

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

        view = TaskCheckinView(user_id, goals)
        await ctx.send("📝 Click a button to mark your tasks as completed!", view=view)
    else:
        await ctx.send("You haven't set any goals yet! Use `!set_goals` first.")

# Run the bot with the token from config.json
bot.run(bot_token)

