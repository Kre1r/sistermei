# ⚖️ Tole Tole Court System

Welcome to the **Tole Tole Court System** – the most sophisticated, automated judicial roleplay environment on Discord, governed by the supreme authority of **Tole Tole Cat**.

This repository contains the autonomous engine that constructs, manages, and maintains your entire legal RP server infrastructure with a single command. No more manual channel management or role hierarchy headaches.

---

## 🏛️ Features
*   **Autonomous Infrastructure:** One-click deployment wipes old channels and builds a fully structured, permissions-optimized legal server.
*   **Dynamic Role Management:** Professional-grade role hierarchy (Judge, Prosecutor, Defense, Jury, etc.) with custom color coding.
*   **Interactive Role-Selection Panel:** User-friendly button-based interface for participants to self-assign their RP roles (Witness, Defendant, Investigator).
*   **Organized Judicial Workflow:** Dedicated categories for:
    *   **Information:** Rules, Announcements, and Lore.
    *   **Community:** General chat and voice lounges.
    *   **Courtroom:** Live trials, witness stands, and public galleries.
    *   **Investigations:** Evidence lockers and case reports.
    *   **Judicial Chambers:** Secure, staff-only deliberation rooms.
*   **GitHub Actions Ready:** Designed for seamless deployment and continuous management via CI/CD.

---

## 🚀 Deployment Instructions

### Prerequisites
1.  **Discord Bot Token:** Create an application via the [Discord Developer Portal](https://discord.com/developers/applications).
2.  **Permissions:** Enable `Server Members Intent` and `Message Content Intent`.
3.  **Administrator:** Invite the bot with `Administrator` permissions.

### Setup
1.  **Configure Secret:** Go to your GitHub repository **Settings > Secrets and variables > Actions**.
2.  **Add Token:** Create a new secret named `DISCORD_BOT_TOKEN` and paste your bot token as the value.
3.  **Run:** Navigate to the Actions tab, select "Run Tole Tole Court Bot," and click **Run workflow**.

### Usage
Once the bot is online, go to your Discord server and use the following command to initialize the court:

`!setup_court`

> ⚠️ **Warning:** This command will delete **ALL** existing channels and categories in your server to ensure a clean slate for the judicial system. Use with caution.

---

## 📜 Legal Notice
*Governed by the paws of Tole Tole Cat. Any attempt to bypass the judicial system will be met with immediate contempt of court.*

---

*Built with passion for the ultimate RP experience.*
