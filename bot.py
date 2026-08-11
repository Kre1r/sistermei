import os
import asyncio
import discord
from discord.ext import commands
from openai import OpenAI

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_api_key) if groq_api_key else None

user_roles_backup = {}
active_trials = set()

class SovereignJudicialView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def toggle_global_role(self, interaction: discord.Interaction, role_name: str):
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            return await interaction.response.send_message(f"⚠️ Judicial Matrix Error: Role `{role_name}` is missing. Run `!setup_court` first.", ephemeral=True)
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Revoked International Clearance: **{role.name}**", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Granted International Clearance: **{role.name}**", ephemeral=True)

    @discord.ui.button(label="🛡️ Defense Attorney", style=discord.ButtonStyle.primary, custom_id="sov_lawyer")
    async def lawyer_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_global_role(interaction, "🛡️ Lead Defense Attorney")

    @discord.ui.button(label="⚖️ Prosecutor", style=discord.ButtonStyle.danger, custom_id="sov_prosecutor")
    async def prosecutor_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_global_role(interaction, "🏛️ Senior Prosecutor")

    @discord.ui.button(label="📜 Jury Member", style=discord.ButtonStyle.success, custom_id="sov_jury")
    async def jury_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_global_role(interaction, "🐾 Jury Foreman")

    @discord.ui.button(label="📢 Public / Witness", style=discord.ButtonStyle.secondary, custom_id="sov_public")
    async def public_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_global_role(interaction, "📢 Witness / Public")


@bot.event
async def on_ready():
    print(f"🔥 [SOVEREIGN CORE V4 - STABLE] Logged in as {bot.user} - Supreme Judge Tole Tole Global System Online")
    bot.add_view(SovereignJudicialView())


@bot.command(name="setup_court")
@commands.has_permissions(administrator=True)
async def setup_court(ctx):
    guild = ctx.guild
    status_msg = await ctx.send("🧹 **[SYSTEM PURGE INITIALIZED]** Wiping legacy server architecture safely...")

    # 1. Güvenli Kanal Temizliği (Rate Limit yemeden)
    for channel in guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(0.3)
        except Exception:
            pass

    # 2. Güvenli Rol Temizliği
    for role in guild.roles:
        if role != guild.default_role and not role.managed and role < guild.me.top_role:
            try:
                await role.delete()
                await asyncio.sleep(0.3)
            except Exception:
                pass

    await status_msg.edit(content="⚡ **[WIPE COMPLETE]** Building pristine sovereign infrastructure with rate-limit protection...")

    try:
        roles_config = {
            "👑 Supreme Judge Tole Tole": (discord.Color.gold(), discord.Permissions.all()),
            "⚖️ Chief Justice": (discord.Color.orange(), discord.Permissions(manage_messages=True, mute_members=True)),
            "🏛️ Senior Prosecutor": (discord.Color.from_rgb(200, 0, 0), discord.Permissions(manage_messages=True)),
            "🛡️ Lead Defense Attorney": (discord.Color.from_rgb(0, 100, 255), discord.Permissions(manage_messages=True)),
            "🐾 Jury Foreman": (discord.Color.green(), discord.Permissions.none()),
            "👤 Defendant / Accused": (discord.Color.lighter_grey(), discord.Permissions.none()),
            "📢 Witness / Public": (discord.Color.default(), discord.Permissions.none()),
            "🔒 Jailed": (discord.Color.dark_theme(), discord.Permissions.none()),
            "🌐 Global Citizen": (discord.Color.blurple(), discord.Permissions(view_channel=True))
        }

        created_roles = {}
        for r_name, (r_color, r_perms) in roles_config.items():
            role = await guild.create_role(name=r_name, color=r_color, permissions=r_perms)
            created_roles[r_name] = role
            await asyncio.sleep(0.4)  # Discord API koruması

        judge_role = created_roles["👑 Supreme Judge Tole Tole"]
        jailed_role = created_roles["🔒 Jailed"]
        citizen_role = created_roles["🌐 Global Citizen"]

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

        jail_overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            jailed_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            judge_role: discord.PermissionOverwrite(view_channel=True, manage_channels=True)
        }

        # Kategoriler ve Kanallar (Gecikmeli güvenli oluşturma)
        cat_info = await guild.create_category("🏛️ ┃ GLOBAL COURT ADMINISTRATION")
        await asyncio.sleep(0.5)
        ch_rules = await guild.create_text_channel("protocols-and-lore", category=cat_info, overwrites=overwrites_public)
        await ch_rules.send("📜 **Tole Tole Global Judiciary Active.** Execute trials using `!justice @user [indictment]`. Strict international English protocol enforced.")

        ch_roles = await guild.create_text_channel("global-role-registry", category=cat_info, overwrites=overwrites_public)
        embed = discord.Embed(title="⚖️ Supreme Court - Sovereign Faction Panel", description="Interact with the encrypted module below to establish your global judicial clearance.", color=discord.Color.gold())
        await ch_roles.send(embed=embed, view=SovereignJudicialView())

        cat_court = await guild.create_category("⚖️ ┃ INTERNATIONAL TRIBUNALS")
        await asyncio.sleep(0.5)
        for i in range(1, 6):
            await guild.create_text_channel(f"courtroom-{i}", category=cat_court, overwrites=overwrites_public)
            await asyncio.sleep(0.3)

        cat_prison = await guild.create_category("⛓️ ┃ FEDERAL PENITENTIARY")
        await asyncio.sleep(0.5)
        await guild.create_text_channel("solitary-confinement", category=cat_prison, overwrites=jail_overwrites, slowmode_delay=10)

        await ctx.send("✅ **Sovereign Rebuilding Complete:** Server wiped clean and successfully built without any rate-limit or build failures.")
    except Exception as e:
        await ctx.send(f"❌ Critical Rebuild Error: {e}")


@bot.command(name="justice")
async def justice(ctx, member: discord.Member, *, crime_description: str):
    if not any(r.name == "👑 Supreme Judge Tole Tole" for r in ctx.author.roles):
        return await ctx.send("❌ **Access Denied:** Sovereign authority required. Only Supreme Judge Tole Tole can open an international tribunal.")

    courtroom = ctx.channel
    if not courtroom.name.startswith("courtroom-"):
        courtroom = discord.utils.get(ctx.guild.text_channels, name="courtroom-1")
        if not courtroom:
            return await ctx.send("⚠️ Operational Error: Trials must be executed within a designated `courtroom-X` node.")

    if courtroom.id in active_trials:
        return await ctx.send("⚠️ Tribunal Conflict: This courtroom node is already locked in an active proceeding.")

    active_trials.add(courtroom.id)

    lawyer_role = discord.utils.get(ctx.guild.roles, name="🛡️ Lead Defense Attorney")
    lawyer_mention = lawyer_role.mention if lawyer_role else "@DefenseAttorney"

    start_embed = discord.Embed(
        title="⚖️ TOLE Tole GLOBAL SUPREME COURT - TRIBUNAL ACTIVE",
        description=f"**Defendant:** {member.mention}\n**Indictment:** {crime_description}\n\n*Supreme Judge Tole Tole demands absolute order. The Defendant and defense counsel ({lawyer_mention}) may present their arguments.*",
        color=discord.Color.dark_red()
    )
    start_embed.set_footer(text="30-Second Unlimited Interrogation Matrix Active. Real-time AI cross-examination enabled in English.")
    await courtroom.send(embed=start_embed)
    await courtroom.send(f"⚖️ **Tole Tole:** The session is live. {member.mention}, address the court immediately. Every word is recorded.")

    chat_history = []
    end_time = asyncio.get_event_loop().time() + 30.0

    def check(m):
        return m.channel == courtroom and (m.author == member or (lawyer_role and lawyer_role in m.author.roles))

    while asyncio.get_event_loop().time() < end_time:
        try:
            msg = await bot.wait_for('message', timeout=1.0, check=check)
            
            role_label = "Defendant" if msg.author == member else "Defense Attorney"
            chat_history.append(f"{role_label} ({msg.author.display_name}): {msg.content}")

            if groq_client:
                mid_prompt = f"""
                You are 'Supreme Judge Tole Tole', a cold, ruthless, elite, absolute, and feared global Supreme Court Judge. 
                Active Indictment: {crime_description}
                Latest statement from {role_label} ({msg.author.display_name}): "{msg.content}"
                
                Respond instantly, sternly, and aggressively in strict professional English. Expose logical flaws, demand hard evidence, show zero mercy, and maintain supreme authority. Keep it strictly to 1-2 sharp, intimidating sentences. No feline or cat references whatsoever.
                """
                res = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": mid_prompt}]
                )
                await courtroom.send(f"⚖️ **Tole Tole:** {res.choices[0].message.content.strip()}")
        except asyncio.TimeoutError:
            continue

    active_trials.discard(courtroom.id)
    formatted_transcript = "\n".join(chat_history) if chat_history else "[The defendant and counsel displayed complete contempt of court by remaining entirely silent.]"

    verdict = "DELAY"
    ai_reason = "Evaluation core compilation failed."

    if groq_client:
        final_prompt = f"""
        You are Supreme Judge Tole Tole, an uncompromising, cold, and supreme global judicial intelligence. Evaluate this completed international trial in strict professional English:
        Defendant: {member.display_name}
        Indictment: {crime_description}
        Verified Trial Transcript:
        {formatted_transcript}

        Select ONLY ONE final sovereign verdict:
        1. GUILTY
        2. INNOCENT
        3. DELAY (Enforces a mandatory 10-second global slowmode across channels due to procedural chaos)

        Format your response strictly as:
        VERDICT: [GUILTY / INNOCENT / DELAY]
        REASON: [Cold, formal, authoritative global judicial ruling in English]
        """
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": final_prompt}]
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
            ai_reason = f"AI Engine Exception: {e}"
    else:
        verdict = "GUILTY" if len(formatted_transcript) < 30 else "DELAY"
        ai_reason = "Simulated sovereign evaluation fallback."

    result_embed = discord.Embed(title="📜 TOLE TOLE GLOBAL - SOVEREIGN JUDICIAL DECREE", color=discord.Color.dark_magenta())
    result_embed.add_field(name="Defendant", value=member.mention, inline=True)
    result_embed.add_field(name="Sovereign Verdict", value=verdict, inline=True)
    result_embed.add_field(name="Supreme Judge Tole Tole's Adjudication", value=ai_reason, inline=False)
    await courtroom.send(embed=result_embed)

    if verdict == "GUILTY":
        jailed_role = discord.utils.get(ctx.guild.roles, name="🔒 Jailed")
        if jailed_role:
            user_roles_backup[member.id] = [r for r in member.roles if r != ctx.guild.default_role and r != jailed_role]
            await member.edit(roles=[jailed_role])
        await courtroom.send(f"🚨 **Sentence Enforced:** {member.mention} has been formally convicted by Supreme Judge Tole Tole and transferred to Federal Solitary Confinement. All security clearance roles have been securely archived.")

    elif verdict == "DELAY":
        for channel in ctx.guild.text_channels:
            try:
                await channel.edit(slowmode_delay=10)
            except Exception:
                pass
        await courtroom.send(f"⏳ **Tribunal Suspended:** Supreme Judge Tole Tole enforces a mandatory **10-second global slowmode** across all channels to re-establish public order.")

    elif verdict == "INNOCENT":
        await courtroom.send(f"✨ **Acquittal Granted:** {member.mention} has been fully exonerated by the tribunal. Case permanently closed.")


@bot.command(name="pardon")
async def pardon(ctx, member: discord.Member):
    if not any(r.name == "👑 Supreme Judge Tole Tole" for r in ctx.author.roles):
        return await ctx.send("❌ **Access Denied:** Only Supreme Judge Tole Tole holds the sovereign royal pardon privilege.")

    jailed_role = discord.utils.get(ctx.guild.roles, name="🔒 Jailed")
    
    original_roles = user_roles_backup.get(member.id, [])
    if jailed_role and jailed_role in member.roles:
        await member.remove_roles(jailed_role)
    
    if original_roles:
        try:
            await member.add_roles(*original_roles)
        except Exception:
            pass
        user_roles_backup.pop(member.id, None)

    for channel in ctx.guild.text_channels:
        try:
            await channel.edit(slowmode_delay=0)
        except Exception:
            pass

    await ctx.send(f"✨ **Sovereign Pardon Issued:** {member.mention} has been released from federal custody, and all archived pre-trial clearances have been fully restored.")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
