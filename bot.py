import os
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


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


@bot.command(name="jail")
async def jail(ctx, member: discord.Member, *, reason="Contempt of Supreme Cat Law"):
    if not any(r.name in ["👑 Supreme Judge Tole Tole", "⚖️ Chief Justice"] for r in ctx.author.roles):
        await ctx.send("❌ Access Denied: Only Supreme Judges and Chief Justices can execute sentences.")
        return

    jailed_role = discord.utils.get(ctx.guild.roles, name="🔒 Jailed")
    if jailed_role:
        await member.add_roles(jailed_role)

    embed = discord.Embed(
        title="⚖️ SENTENCE TO THE CAT CELL",
        description=f"**{member.mention}** has been locked up behind bars under Tole Tole's strict judgment!",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text="Silence echoes in the dark cell.")
    await ctx.send(embed=embed)


@bot.command(name="pardon")
async def pardon(ctx, member: discord.Member):
    if not any(r.name in ["👑 Supreme Judge Tole Tole"] for r in ctx.author.roles):
        await ctx.send("❌ Access Denied: Only Supreme Judge Tole Tole can grant freedom.")
        return

    jailed_role = discord.utils.get(ctx.guild.roles, name="🔒 Jailed")
    if jailed_role and jailed_role in member.roles:
        await member.remove_roles(jailed_role)
    
    await ctx.send(f"✨ **{member.mention}** has been released from the cell by the supreme mercy of Tole Tole!")


@bot.command(name="evidence")
async def evidence(ctx):
    if not any(r.name in ["🕵️ Detective / Investigator", "👑 Supreme Judge Tole Tole", "🏛️ Senior Prosecutor"] for r in ctx.author.roles):
        await ctx.send("❌ Access Denied: Only Investigators, Judges, and Prosecutors can inspect the files.")
        return

    evidence_list = [
        "🐾 A glowing supernatural paw print was found at the crime scene.",
        "🐟 A half-eaten sacred fish outline indicating foul play.",
        "📜 A classified transcript showing secret bribes under the rug.",
        "🔍 Zero forensic residue detected. The criminal covered their tracks well.",
    ]
    chosen = random.choice(evidence_list)
    
    embed = discord.Embed(
        title="📁 EVIDENCE INVESTIGATION REPORT",
        description=chosen,
        color=discord.Color.dark_grey()
    )
    await ctx.send(embed=embed)


@bot.command(name="setup_court")
@commands.has_permissions(administrator=True)
async def setup_court(ctx):
    guild = ctx.guild
    await ctx.send("⚖️ **[Tole Tole Supreme Court]** Purging channels and roles, reconstructing the ultimate judicial universe...")

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
        }

        created_roles = {}
        for r_name, (r_color, r_perms) in roles_config.items():
            role = await guild.create_role(name=r_name, color=r_color, permissions=r_perms)
            created_roles[r_name] = role

        judge_role = created_roles["👑 Supreme Judge Tole Tole"]
        public_role = created_roles["📢 Witness / Public"]
        jailed_role = created_roles["🔒 Jailed"]

        overwrites_public = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            public_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            judge_role: discord.PermissionOverwrite(view_channel=True, manage_channels=True),
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
        await ch_rules.send(
            "📜 **THE LAWS OF TOLE TOLE**\n\n"
            "1. Supreme Judge Tole Tole's word is absolute truth.\n"
            "2. No whispering false testimonies during active trials.\n"
            "3. Disrespecting the claws of justice results in immediate banishment to the cell."
        )

        ch_ann = await guild.create_text_channel("announcements", category=cat_info, overwrites=overwrites_public)
        await ch_ann.send("📢 **Official Court Broadcast:** The court is now in session. Check your roles and prepare for trial!")

        roles_channel = await guild.create_text_channel("roles-selection", category=cat_info, overwrites=overwrites_public)
        embed = discord.Embed(
            title="🐾 Tole Tole Supreme Court - Role Selection",
            description="Claim your faction within the judiciary system by clicking below.\n\n*Execute `!jail`, `!evidence`, and `!pardon` based on your authority.*",
            color=discord.Color.gold(),
        )
        await roles_channel.send(embed=embed, view=RoleSelectView())

        cat_cell = await guild.create_category("⛓️ ┃ PRISON SYSTEM")
        ch_jail = await guild.create_text_channel("the-cat-cell", category=cat_cell, overwrites=jail_overwrites, slowmode_delay=5)
        await ch_jail.send("⛓️ **Welcome to the Cat Cell.** You are imprisoned here under strict supervision. A 5-second slowmode is enforced.")

        cat_community = await guild.create_category("🐾 ┃ TOLE TOLE SANCTUARY")
        ch_gen = await guild.create_text_channel("general-chat", category=cat_community, overwrites=overwrites_public)
        await ch_gen.send("💬 Welcome to the sanctuary lounge. Discuss fandom theories under the watchful eye of Tole Tole.")
        
        await guild.create_text_channel("fandom-discussion", category=cat_community, overwrites=overwrites_public)
        await guild.create_text_channel("bot-commands", category=cat_community, overwrites=overwrites_public)
        await guild.create_voice_channel("Purr Lounge 1 (VC)", category=cat_community, overwrites=overwrites_public)
        await guild.create_voice_channel("Purr Lounge 2 (VC)", category=cat_community, overwrites=overwrites_public)

        cat_courtroom = await guild.create_category("⚖️ ┃ THE GRAND COURTROOMS")
        ch_alpha = await guild.create_text_channel("courtroom-alpha", category=cat_courtroom, overwrites=overwrites_public)
        await ch_alpha.send("⚖️ **Courtroom Alpha is active.** Silence in the room! Trial proceedings are starting.")
        
        await guild.create_text_channel("courtroom-beta", category=cat_courtroom, overwrites=overwrites_public)
        await guild.create_text_channel("witness-stand", category=cat_courtroom, overwrites=overwrites_public)
        await guild.create_text_channel("evidence-locker", category=cat_courtroom, overwrites=overwrites_public)
        await guild.create_voice_channel("Trial Audio Alpha (VC)", category=cat_courtroom, overwrites=overwrites_public)
        await guild.create_voice_channel("Trial Audio Beta (VC)", category=cat_courtroom, overwrites=overwrites_public)
        await guild.create_voice_channel("Audience Gallery (VC)", category=cat_courtroom, overwrites=overwrites_public)

        cat_cases = await guild.create_category("📁 ┃ EVIDENCE & CASE FILES")
        await guild.create_text_channel("crime-scene-reports", category=cat_cases, overwrites=overwrites_public)
        await guild.create_text_channel("active-investigations", category=cat_cases, overwrites=overwrites_public)
        await guild.create_text_channel("verdicts-and-sentences", category=cat_cases, overwrites=overwrites_public)

        cat_staff = await guild.create_category("🔒 ┃ JUDICIAL CHAMBERS")
        await guild.create_text_channel("judge-tole-tole-office", category=cat_staff, overwrites=overwrites_locked)
        await guild.create_text_channel("prosecution-defense-strategy", category=cat_staff, overwrites=overwrites_locked)
        await guild.create_text_channel("jury-deliberation-room", category=cat_staff, overwrites=overwrites_locked)
        await guild.create_voice_channel("High Council Meeting (VC)", category=cat_staff, overwrites=overwrites_locked)

    except Exception as e:
        print(f"Error during setup: {e}")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
