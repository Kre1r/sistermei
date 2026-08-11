import os
import asyncio
import random
import discord
from discord.ext import commands
from openai import OpenAI

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Groq API Configuration
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    groq_client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=groq_api_key
    )
else:
    groq_client = None


class RoleSelectView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def assign_role(self, interaction: discord.Interaction, role_name: str):
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(f"❌ Revoked: **{role.name}**", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ Granted: **{role.name}**", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Role not found! Initialize with `!setup_court`.", ephemeral=True)

    @discord.ui.button(label="Witness / Public", style=discord.ButtonStyle.secondary, custom_id="role_witness")
    async def witness_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_role(interaction, "📢 Witness / Public")

    @discord.ui.button(label="Defendant", style=discord.ButtonStyle.danger, custom_id="role_defendant")
    async def defendant_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_role(interaction, "👤 Defendant / Accused")

    @discord.ui.button(label="Investigator", style=discord.ButtonStyle.primary, custom_id="role_investigator")
    async def investigator_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_role(interaction, "🕵️ Detective / Investigator")

    @discord.ui.button(label="Defense Attorney", style=discord.ButtonStyle.success, custom_id="role_lawyer")
    async def lawyer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_role(interaction, "🛡️ Lead Defense Attorney")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(RoleSelectView())


@bot.command(name="justice")
async def justice(ctx, member: discord.Member, *, crime_description="General Suspicion"):
    if not any(r.name in ["👑 Supreme Judge Tole Tole", "⚖️ Chief Justice", "🕵️ Detective / Investigator"] for r in ctx.author.roles):
        await ctx.send("❌ Access Denied: You don't have authority to initiate a divine trial.")
        return

    courtroom = discord.utils.get(ctx.guild.text_channels, name="courtroom-alpha")
    if not courtroom:
        await ctx.send("⚠️ 'courtroom-alpha' channel not found! Run `!setup_court` first.")
        return

    lawyer_role = discord.utils.get(ctx.guild.roles, name="🛡️ Lead Defense Attorney")
    lawyer_mention = lawyer_role.mention if lawyer_role else "@DefenseAttorney"

    embed = discord.Embed(
        title="⚖️ THE DIVINE TRIAL HAS BEGUN",
        description=f"**{member.mention}** is on trial! Defense Attorney ({lawyer_mention}), prepare to defend your client.",
        color=discord.Color.orange()
    )
    embed.add_field(name="Accusation / Crime", value=crime_description, inline=False)
    embed.set_footer(text="30-second interactive court session has started. Defendant and Lawyers can chat freely!")
    
    await courtroom.send(embed=embed)
    await courtroom.send(f"⚖️ Supreme Judge Tole Tole demands answers from {member.mention} and attorney {lawyer_mention}!")

    # 30-second interactive chat collection loop
    chat_history = []
    end_time = asyncio.get_event_loop().time() + 30.0

    def check(m):
        return m.channel == courtroom and (m.author == member or (lawyer_role and lawyer_role in m.author.roles))

    while asyncio.get_event_loop().time() < end_time:
        remaining = int(end_time - asyncio.get_event_loop().time())
        try:
            msg = await bot.wait_for('message', timeout=min(5.0, max(1.0, remaining)), check=check)
            role_label = "Defendant" if msg.author == member else "Defense Attorney"
            chat_history.append(f"{role_label} ({msg.author.display_name}): {msg.content}")
            
            # Interactive mid-trial cat judge response if Groq is available
            if groq_client and len(chat_history) % 2 == 1:
                mid_prompt = f"""
                You are Tole Tole, a strict, sassy supreme cat judge. 
                Trial Crime: {crime_description}
                Live courtroom dialogue so far:
                {chr(10).join(chat_history)}
                
                Write a short, sharp, sarcastic or intimidating sentence reacting to the latest defense statement as the judge. Keep it under 2 sentences.
                """
                res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": mid_prompt}])
                await courtroom.send(f"🐾 **Judge Tole Tole:** {res.choices[0].message.content.strip()}")
        except asyncio.TimeoutError:
            continue

    formatted_defense = "\n".join(chat_history) if chat_history else "[No defense or lawyer statement provided - Total Silence]"

    # Final AI Evaluation
    verdict = "DELAY"
    ai_reason = "AI evaluation fallback."

    if groq_client:
        prompt = f"""
        You are Tole Tole, a strict and supreme cat judge. Evaluate the completed trial:
        Accused: {member.display_name}
        Crime/Accusation: {crime_description}
        Full Court Defense Transcript:
        {formatted_defense}

        Choose ONLY ONE verdict:
        1. GUILTY
        2. INNOCENT
        3. DELAY (Needs 10-second slowmode penalty across channels)

        Format strictly as:
        VERDICT: [GUILTY / INNOCENT / DELAY]
        REASON: [Short dramatic cat-judge explanation]
        """
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            ai_output = response.choices[0].message.content.strip()
            if "GUILTY" in ai_output.upper():
                verdict = "GUILTY"
            elif "INNOCENT" in ai_output.upper():
                verdict = "INNOCENT"
            else:
                verdict = "DELAY"
            ai_reason = ai_output
        except Exception as e:
            ai_reason = f"Groq API Error: {e}"
    else:
        verdict = "GUILTY" if len(formatted_defense) < 20 else "DELAY"
        ai_reason = "Simulated verdict."

    result_embed = discord.Embed(title="📜 FINAL JUDGMENT VERDICT", color=discord.Color.purple())
    result_embed.add_field(name="Defendant", value=member.mention, inline=True)
    result_embed.add_field(name="Final Verdict", value=verdict, inline=True)
    result_embed.add_field(name="Judge's Ruling", value=ai_reason, inline=False)
    await courtroom.send(embed=result_embed)

    if verdict == "GUILTY":
        jailed_role = discord.utils.get(ctx.guild.roles, name="🔒 Jailed")
        if jailed_role:
            await member.add_roles(jailed_role)
        await courtroom.send(f"🚨 **{member.mention} has been sentenced to the Cat Cell!**")

    elif verdict == "DELAY":
        for channel in ctx.guild.text_channels:
            try:
                await channel.edit(slowmode_delay=10)
            except Exception:
                pass
        await courtroom.send(f"⏳ **Trial Borderline!** Supreme Tole Tole enforces a **10-second slowmode** across all channels.")

    elif verdict == "INNOCENT":
        jailed_role = discord.utils.get(ctx.guild.roles, name="🔒 Jailed")
        if jailed_role and jailed_role in member.roles:
            await member.remove_roles(jailed_role)
        await courtroom.send(f"✨ **{member.mention} has been declared innocent!**")


@bot.command(name="pardon")
async def pardon(ctx, member: discord.Member):
    if not any(r.name in ["👑 Supreme Judge Tole Tole"] for r in ctx.author.roles):
        await ctx.send("❌ Access Denied: Only Supreme Judge Tole Tole can grant freedom.")
        return

    jailed_role = discord.utils.get(ctx.guild.roles, name="🔒 Jailed")
    if jailed_role and jailed_role in member.roles:
        await member.remove_roles(jailed_role)
    
    for channel in ctx.guild.text_channels:
        try:
            await channel.edit(slowmode_delay=0)
        except Exception:
            pass

    await ctx.send(f"✨ **{member.mention}** has been pardoned and channel slowmodes have been lifted!")


@bot.command(name="setup_court")
@commands.has_permissions(administrator=True)
async def setup_court(ctx):
    guild = ctx.guild
    await ctx.send("⚖️ **[Tole Tole Supreme Court]** Purging channels & roles, building the full AI judiciary universe...")

    try:
        for channel in guild.channels:
            try:
                await channel.delete()
            except:
                pass

        for role in guild.roles:
            if role != guild.default_role and not role.managed and role < guild.me.top_role:
                try:
                    await role.delete()
                except:
                    pass

        roles_config = {
            "👑 Supreme Judge Tole Tole": (discord.Color.gold(), discord.Permissions.all()),
            "⚖️ Chief Justice": (discord.Color.orange(), discord.Permissions(manage_messages=True, mute_members=True)),
            "🏛️ Senior Prosecutor": (discord.Color.from_rgb(200, 0, 0), discord.Permissions(manage_messages=True)),
            "🛡️ Lead Defense Attorney": (discord.Color.from_rgb(0, 100, 255), discord.Permissions(manage_messages=True)),
            "📜 Court Clerk": (discord.Color.teal(), discord.Permissions.none()),
            "🐾 Jury Foreman": (discord.Color.green(), discord.Permissions.none()),
            "🕵️ Detective / Investigator": (discord.Color.dark_grey(), discord.Permissions(view_audit_log=True)),
            "👤 Defendant / Accused": (discord.Color.lighter_grey(), discord.Permissions.none()),
            "📢 Witness / Public": (discord.Color.default(), discord.Permissions.none()),
            "🔒 Jailed": (discord.Color.dark_theme(), discord.Permissions.none()),
            "🌐 Citizen / Everyone": (discord.Color.blurple(), discord.Permissions(view_channel=True)),
        }

        created_roles = {}
        for r_name, (r_color, r_perms) in roles_config.items():
            role = await guild.create_role(name=r_name, color=r_color, permissions=r_perms)
            created_roles[r_name] = role

        judge_role = created_roles["👑 Supreme Judge Tole Tole"]
        jailed_role = created_roles["🔒 Jailed"]
        citizen_role = created_roles["🌐 Citizen / Everyone"]

        for member in guild.members:
            try:
                await member.add_roles(citizen_role)
            except:
                pass

        overwrites_public = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            citizen_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            jailed_role: discord.PermissionOverwrite(view_channel=False)
        }

        overwrites_locked = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            judge_role: discord.PermissionOverwrite(view_channel=True),
            jailed_role: discord.PermissionOverwrite(view_channel=False)
        }

        jail_overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            jailed_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            judge_role: discord.PermissionOverwrite(view_channel=True, manage_channels=True)
        }

        cat_info = await guild.create_category("🏛️ ┃ COURT INFORMATION")
        ch_rules = await guild.create_text_channel("rules-and-lore", category=cat_info, overwrites=overwrites_public)
        await ch_rules.send("📜 **INTERACTIVE AI JUSTICE:** Use `!justice @user [crime]` to start a trial. Defendants and Lawyers can chat during the 30-second defense phase!")

        roles_channel = await guild.create_text_channel("roles-selection", category=cat_info, overwrites=overwrites_public)
        embed = discord.Embed(
            title="🐾 Tole Tole Supreme Court - Role Selection",
            description="Claim your faction by clicking below (including Defense Attorney!).",
            color=discord.Color.gold(),
        )
        await roles_channel.send(embed=embed, view=RoleSelectView())

        cat_cell = await guild.create_category("⛓️ ┃ PRISON SYSTEM")
        ch_jail = await guild.create_text_channel("the-cat-cell", category=cat_cell, overwrites=jail_overwrites, slowmode_delay=5)
        await ch_jail.send("⛓️ **The Cat Cell:** Imprisoned users stay here.")

        cat_community = await guild.create_category("🐾 ┃ TOLE TOLE SANCTUARY")
        await guild.create_text_channel("general-chat", category=cat_community, overwrites=overwrites_public)
        await guild.create_text_channel("bot-commands", category=cat_community, overwrites=overwrites_public)

        cat_courtroom = await guild.create_category("⚖️ ┃ THE GRAND COURTROOMS")
        await guild.create_text_channel("courtroom-alpha", category=cat_courtroom, overwrites=overwrites_public)
        await guild.create_text_channel("courtroom-beta", category=cat_courtroom, overwrites=overwrites_public)

        cat_staff = await guild.create_category("🔒 ┃ JUDICIAL CHAMBERS")
        await guild.create_text_channel("judge-tole-tole-office", category=cat_staff, overwrites=overwrites_locked)

        await ctx.send("✅ **Setup Complete!** All roles, categories and channels successfully created.")

    except Exception as e:
        print(f"Error during setup: {e}")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
