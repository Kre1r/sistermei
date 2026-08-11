import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# --- BUTTON VIEW FOR SELF-ASSIGNABLE ROLES ---
class RoleSelectView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  async def assign_role(
      self, interaction: discord.Interaction, role_name: str
  ):
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role:
      if role in interaction.user.roles:
        await interaction.user.remove_roles(role)
        await interaction.response.send_message(
            f"❌ Removed role: **{role.name}**", ephemeral=True
        )
      else:
        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            f"✅ Assigned role: **{role.name}**", ephemeral=True
        )
    else:
      await interaction.response.send_message(
          "⚠️ Role not found! Please ask an administrator to run `!setup_court`"
          " first.",
          ephemeral=True,
      )

  @discord.ui.button(
      label="🐾 Witness / Public",
      style=discord.ButtonStyle.secondary,
      custom_id="role_witness",
  )
  async def witness_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.assign_role(interaction, "📢 Witness / Public")

  @discord.ui.button(
      label="👤 Defendant",
      style=discord.ButtonStyle.danger,
      custom_id="role_defendant",
  )
  async def defendant_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.assign_role(interaction, "👤 Defendant / Accused")

  @discord.ui.button(
      label="🕵️ Investigator",
      style=discord.ButtonStyle.primary,
      custom_id="role_investigator",
  )
  async def investigator_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.assign_role(interaction, "🕵️ Detective / Investigator")


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user} (ID: {bot.user.id})")
  # Persistent view for buttons to keep working after bot restarts
  bot.add_view(RoleSelectView())
  print("The advanced court system is ready!")


@bot.command(name="setup_court")
@commands.has_permissions(administrator=True)
async def setup_court(ctx):
  guild = ctx.guild
  await ctx.send(
      "⚖️ **[Tole Tole Cat's Court]** Wiping server and building the ultimate"
      " advanced judicial system..."
  )

  try:
    # ----------------------------------------------------
    # 0. PURGE EXISTING CHANNELS & CATEGORIES
    # ----------------------------------------------------
    for channel in guild.channels:
      try:
        await channel.delete(reason="Advanced Court Setup Reset")
      except Exception as e:
        print(f"Skipped channel {channel.name}: {e}")

    # ----------------------------------------------------
    # 1. ADVANCED ROLES SETUP
    # ----------------------------------------------------
    roles_config = {
        "👑 Supreme Judge Tole Tole": discord.Color.gold(),
        "⚖️ Chief Justice": discord.Color.orange(),
        "🏛️ Senior Prosecutor": discord.Color.from_rgb(200, 0, 0),
        "🛡️ Lead Defense Attorney": discord.Color.from_rgb(0, 100, 255),
        "📜 Court Clerk": discord.Color.teal(),
        "🐾 Jury Foreman": discord.Color.green(),
        "🕵️ Detective / Investigator": discord.Color.dark_grey(),
        "👤 Defendant / Accused": discord.Color.lighter_grey(),
        "📢 Witness / Public": discord.Color.default(),
    }

    created_roles = {}
    for r_name, r_color in roles_config.items():
      role = await guild.create_role(
          name=r_name, color=r_color, reason="Advanced Court Setup"
      )
      created_roles[r_name] = role

    # ----------------------------------------------------
    # 2. PERMISSIONS CONFIG
    # ----------------------------------------------------
    overwrites_public = {
        guild.default_role: discord.PermissionOverwrite(view_channel=True)
    }
    overwrites_locked = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False)
    }

    # ----------------------------------------------------
    # 3. CATEGORIES & CHANNELS CREATION
    # ----------------------------------------------------

    # --- CATEGORY: 🏛️ COURT INFORMATION & LORE ---
    cat_info = await guild.create_category("🏛️ ┃ COURT INFORMATION")
    await guild.create_text_channel(
        "welcome-and-lore", category=cat_info, overwrites=overwrites_public
    )
    await guild.create_text_channel(
        "official-announcements",
        category=cat_info,
        overwrites={
            guild.default_role: discord.PermissionOverwrite(
                view_channel=True, send_messages=False
            )
        },
    )
    await guild.create_text_channel(
        "court-constitution", category=cat_info, overwrites=overwrites_public
    )

    roles_channel = await guild.create_text_channel(
        "roles-selection", category=cat_info, overwrites=overwrites_public
    )

    # Send the interactive role selection panel embed with buttons
    embed = discord.Embed(
        title="🐾 Tole Tole Court - Role Selection",
        description=(
            "Welcome to the judicial system managed by the Supreme Judge Tole"
            " Tole!\n\nClick the buttons below to assign or remove your public"
            " role for the roleplay:"
        ),
        color=discord.Color.gold(),
    )
    embed.add_field(
        name="Roles Available:",
        value=(
            "• **Witness / Public**: Regular attendees and witnesses.\n•"
            " **Defendant**: Those facing trial under Tole Tole's law.\n•"
            " **Investigator**: Detectives gathering evidence."
        ),
        inline=False,
    )
    embed.set_footer(text="Powered by Tole Tole Cat's Law System")
    await roles_channel.send(embed=embed, view=RoleSelectView())

    # --- CATEGORY: 🐾 COMMUNITY & LOUNGE ---
    cat_community = await guild.create_category("🐾 ┃ TOLE TOLE SANCTUARY")
    await guild.create_text_channel(
        "general-chat", category=cat_community, overwrites=overwrites_public
    )
    await guild.create_text_channel(
        "fandom-discussion", category=cat_community, overwrites=overwrites_public
    )
    await guild.create_text_channel(
        "bot-commands", category=cat_community, overwrites=overwrites_public
    )
    await guild.create_voice_channel(
        "Purr Lounge 1 (VC)",
        category=cat_community,
        overwrites=overwrites_public,
    )
    await guild.create_voice_channel(
        "Purr Lounge 2 (VC)",
        category=cat_community,
        overwrites=overwrites_public,
    )

    # --- CATEGORY: ⚖️ LIVE COURTROOMS (RP AREA) ---
    cat_courtroom = await guild.create_category("⚖️ ┃ THE GRAND COURTROOMS")
    await guild.create_text_channel(
        "court-calendar", category=cat_courtroom, overwrites=overwrites_public
    )
    await guild.create_text_channel(
        "courtroom-alpha", category=cat_courtroom, overwrites=overwrites_public
    )
    await guild.create_text_channel(
        "courtroom-beta", category=cat_courtroom, overwrites=overwrites_public
    )
    await guild.create_text_channel(
        "witness-stand", category=cat_courtroom, overwrites=overwrites_public
    )
    await guild.create_voice_channel(
        "Active Trial Audio (VC)",
        category=cat_courtroom,
        overwrites=overwrites_public,
    )
    await guild.create_voice_channel(
        "Audience Gallery (VC)",
        category=cat_courtroom,
        overwrites=overwrites_public,
    )

    # --- CATEGORY: 📁 INVESTIGATION & CASE FILES ---
    cat_cases = await guild.create_category("📁 ┃ EVIDENCE & CASE FILES")
    await guild.create_text_channel(
        "crime-scene-reports",
        category=cat_cases,
        overwrites=overwrites_public,
    )
    await guild.create_text_channel(
        "evidence-locker", category=cat_cases, overwrites=overwrites_public
    )
    await guild.create_text_channel(
        "verdicts-and-sentences",
        category=cat_cases,
        overwrites=overwrites_public,
    )

    # --- CATEGORY: 🔒 JUDICIAL CHAMBERS (STAFF ONLY) ---
    cat_staff = await guild.create_category("🔒 ┃ JUDICIAL CHAMBERS")
    await guild.create_text_channel(
        "judge-tole-tole-chambers",
        category=cat_staff,
        overwrites=overwrites_locked,
    )
    await guild.create_text_channel(
        "prosecution-defense-strategy",
        category=cat_staff,
        overwrites=overwrites_locked,
    )
    await guild.create_text_channel(
        "jury-deliberation-room",
        category=cat_staff,
        overwrites=overwrites_locked,
    )
    await guild.create_voice_channel(
        "High Council Meeting (VC)",
        category=cat_staff,
        overwrites=overwrites_locked,
    )

  except Exception as e:
    print(f"❌ Error during advanced setup: {e}")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
