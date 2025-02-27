import discord
import random
import bot_classes.taskButtons as taskButtons
from bot_classes.dataManager import data, save_data  

# CLASS:
class TaskCheckinView(discord.ui.View):

    def __init__(self, user_id, tasks):
        super().__init__(timeout=86400)  # Buttons stay active for 24 hours
        self.user_id = user_id
        self.tasks = tasks
        self.completed_tasks = set()

        for i, task in enumerate(tasks):
            self.add_item(taskButtons.TaskButton(label=task, custom_id=f"task_{i}", view=self))

    async def task_completed(self, interaction: discord.Interaction, task_id): 
        """Handles task completion when a user clicks a button."""
        if interaction.user.id != int(self.user_id):  #check for interaction object if the id of user object is the same as the user who created the task
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