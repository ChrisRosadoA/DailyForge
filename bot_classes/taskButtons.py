import discord

# CLASS: 
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