from discord.ext import commands, tasks
import json

import time


class reminderTask(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

        self.reminder_task.start()

    @tasks.loop(seconds=5)
    async def reminder_task(self):
        with open("local_only/reminders.json", "r") as f:
            data = json.load(f)

        for user in data:
            for remindertime, reminderstr in zip(data[user], data[user].values()):
                if round(time.time()) >= float(remindertime):
                    
                    userobj = await self.miku.fetch_user(user)
                    await userobj.send(f"**Reminder:** {reminderstr}")
                    data[user].pop(remindertime)
                    with open("local_only/reminders.json", "w") as f:
                        json.dump(data, f)

                    await self.reminder_task()
                    return


async def setup(bot):
    await bot.add_cog(reminderTask(bot))
