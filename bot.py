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
                await interaction.response.send_message(f"❌ Removed role: **{role.name}**", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ Assigned role: **{role.name}**", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Role not found! Run `!setup_court` first.", ephemeral=True)

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
async def jail(ctx, member: discord.Member, *, reason="Contempt of Court"):
    if not any(r.name in ["👑 Supreme Judge Tole Tole", "⚖️ Chief Justice"] for r in ctx.author.roles):
        await ctx.send("❌ Only Supreme Judges and Chief Justices can use this command!")
        return

    defendant_role = discord.utils.get(ctx.guild.roles, name="👤 Defendant / Accused")
    if defendant_role:
        await member.add_roles(defendant_role)

    await ctx.send(f"🚨 **{member.mention}** has been found guilty and imprisoned by Supreme Judge Tole Tole!\n📌 **Reason:** {reason}")


@bot.command(name="evidence")
async def evidence(ctx):
    if not any(r.name in ["🕵️ Detective / Investigator", "👑 Supreme Judge Tole Tole"] for r in ctx.author.roles):
        await ctx.send("❌ Only Investigators and Judges can search for evidence!")
        return

    evidence_list = [
        "🐾 A secret paw print left by Tole Tole was discovered!",
        "🔍 A suspicious fish bone was recovered from the crime scene.",
        "📜 A torn piece of a classified court transcript was found.",
        "❌ No evidence could be recovered in this sector.",
    ]
    chosen = random.choice(evidence_list)
    await ctx.send(f"🕵️ **Evidence Search Result:** {chosen}")


@bot.command(name="setup_court")
@commands.has_permissions(administrator=True)
async def setup_court(ctx):
    guild = ctx.guild
    await ctx.send("⚖️ **[Tole Tole Cat's Court]** Wiping server and building the full judicial infrastructure...")

    try:
        for channel in guild.channels:
            try:
                await channel.delete()
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
        }

        created_roles = {}
        for r_name, (r_color, r_perms) in roles_config.items():
            role = await guild.create_role(name=r_name, color=r_color, permissions=r_perms)
            created_roles[r_name] = role

        judge_role = created_roles["👑 Supreme Judge Tole Tole"]
        public_role = created_roles["📢 Witness / Public"]

        overwrites_public = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            public_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            judge_role: discord.PermissionOverwrite(view_channel=True, manage_channels=True)
        }

        overwrites_locked = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            judge_role: discord.PermissionOverwrite(view_channel=True)
        }

        cat_info = await guild.create_category("🏛️ ┃ COURT INFORMATION")
        await guild.create_text_channel("rules-and-lore", category=cat_info, overwrites=overwrites_public)
        await guild.create_text_channel("announcements", category=cat_info, overwrites=overwrites_public)
        roles_channel = await guild.create_text_channel("roles-selection", category=cat_info, overwrites=overwrites_public)

        embed = discord.Embed(
            title="🐾 Tole Tole Court - Role Selection",
            description="Click the buttons below to assign or remove your role!\n\n*Note: Roles grant access and features like !jail and !evidence.*",
            color=discord.Color.gold(),
        )
        await roles_channel.send(embed=embed, view=RoleSelectView())

        cat_community = await guild.create_category("🐾 ┃ TOLE TOLE SANCTUARY")
        await guild.create_text_channel("general-chat", category=cat_community, overwrites=overwrites_public)
        await guild.create_text_channel("bot-commands", category=cat_community, overwrites=overwrites_public)
        await guild.create_voice_channel("Purr Lounge (VC)", category=cat_community, overwrites=overwrites_public)

        cat_courtroom = await guild.create_category("⚖️ ┃ THE GRAND COURTROOMS")
        await guild.create_text_channel("courtroom-main", category=cat_courtroom, overwrites=overwrites_public)
        await guild.create_text_channel("evidence-locker", category=cat_courtroom, overwrites=overwrites_public)
        await guild.create_voice_channel("Trial Audio (VC)", category=cat_courtroom, overwrites=overwrites_public)

        cat_staff = await guild.create_category("🔒 ┃ JUDICIAL CHAMBERS")
        await guild.create_text_channel("private-deliberation", category=cat_staff, overwrites=overwrites_locked)
        await guild.create_voice_channel("Chambers (VC)", category=cat_staff, overwrites=overwrites_locked)

    except Exception as e:
        print(f"Error during setup: {e}")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
