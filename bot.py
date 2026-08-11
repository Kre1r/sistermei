import os
import random
import discord
from discord.ext import commands
from openai import OpenAI

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Groq API Configuration (Groq uses OpenAI compatible client)
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

    embed = discord.Embed(
        title="⚖️ THE DIVINE TRIAL HAS BEGUN",
        description=f"**{member.mention}**, Supreme Judge Tole Tole and the Groq AI Tribunal summon you to answer for your deeds!",
        color=discord.Color.orange()
    )
    embed.add_field(name="Accusation / Crime", value=crime_description, inline=False)
    embed.set_footer(text="You have 30 seconds to type your defense message right here!")
    
    await courtroom.send(embed=embed)
    await courtroom.send(f"{member.mention}, speak now! Defend yourself against this accusation.")

    def check(m):
        return m.author == member and m.channel == courtroom

    try:
        defense_msg = await bot.wait_for('message', timeout=30.0, check=check)
        defense_text = defense_msg.content
    except Exception:
        defense_text = "[No defense provided - Silence is treated as guilt or disrespect]"

    verdict = "DELAY"
    ai_reason = "AI evaluation fallback."

    if groq_client:
        prompt = f"""
        You are Tole Tole, a strict and supreme cat judge. Evaluate the following trial:
        Accused: {member.display_name}
        Crime/Accusation: {crime_description}
        Defense Statement: {defense_text}

        You must choose ONLY ONE of these three verdicts:
        1. GUILTY (Deserves jail)
        2. INNOCENT (Free to go)
        3. DELAY (Suspicious/Delay/Inconclusive - needs a 10-second slowmode penalty across channels to calm down)

        Format your response strictly as:
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
        verdict = "GUILTY" if len(defense_text) < 10 else "DELAY"
        ai_reason = "Simulated verdict due to missing Groq API key configuration."

    result_embed = discord.Embed(title="📜 GROQ AI JUDGMENT VERDICT", color=discord.Color.purple())
    result_embed.add_field(name="Defendant", value=member.mention, inline=True)
    result_embed.add_field(name="Final Verdict", value=verdict, inline=True)
    result_embed.add_field(name="Judge's Notes", value=ai_reason, inline=False)
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
        await courtroom.send(f"⏳ **Trial Suspended / Borderline Case!** Supreme Tole Tole enforces a **10-second slowmode** across all channels.")

    elif verdict == "INNOCENT":
        jailed_role = discord.utils.get(ctx.guild.roles, name="🔒 Jailed")
        if jailed_role and jailed_role in member.roles:
            await member.remove_roles(jailed_role)
        await courtroom.send(f"✨ **{member.mention} has been declared innocent!** Walk free under the sun.")


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
    await ctx.send("⚖️ **[Tole Tole Supreme Court]** Purging channels & roles, building the Groq AI-powered judiciary universe...")

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
        await ch_rules.send("📜 **GROQ AI JUSTICE SYSTEM ACTIVE:** Use `!justice @user [crime]` to put someone on trial. The AI will evaluate their defense!")

        roles_channel = await guild.create_text_channel("roles-selection", category=cat_info, overwrites=overwrites_public)
        embed = discord.Embed(
            title="🐾 Tole Tole Supreme Court - Role Selection",
            description="Claim your faction by clicking below.",
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

        await ctx.send("✅ **Setup Complete!** All channels and roles created. Everyone has been granted the general view role.")

    except Exception as e:
        print(f"Error during setup: {e}")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
