
# Fireteam Photo Creator 

This script automates the process of collecting and organizing Destiny 2 player profile data, generating combined images of guardian profiles effortlessly.

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Downloading and Installing Python](#downloading-and-installing-python)
  - [Downloading Necessary Libraries](#downloading-necessary-libraries)
- [Configuration](#-configuration)
- [Running the Script](#-running-the-script)
- [License](#-license)

## ⚙️ Prerequisites

- A PC running Windows
- An active internet connection
- Destiny 2
- A Bungie.net API key [Bungie API Key](https://www.bungie.net/en/Application/Create)
	- Log in with Bungie account and click the link again
	- Fill out "Application Name" with whatever you want as long as its not taken
	- Scroll down and and click "I agree to abide by the Terms of Use for the Bungie.net API" and click Create New App

## 💾 Installation

### Downloading and Installing Python

1. **Download Python:**
   - Visit the official Python website: [Python Download](https://www.python.org/downloads/)
   - Download the latest stable release suitable for your operating system (Windows).

2. **Install Python:**
   - Run the installer.
   - **Important:** Check the box that says "Add Python to PATH" before clicking "Install Now".
   - Follow the installation steps until completion.

3. **Verify Installation:**
   - Open Command Prompt (cmd.exe in the search bar).
   - Type `python --version` and press Enter. You should see the installed Python version.

### Downloading Necessary Libraries

To run the script, you need to install the required libraries. Open Command Prompt ('cmd.exe' in the search bar) and copy and paste the following commands:

     
     pip install aiohttp pillow pyautogui


This will install:
- \`aiohttp\` for asynchronous HTTP requests
- \`pillow\` for image processing
- \`pyautogui\` for GUI automation

## 🛠️ Configuration

1. **Add Configuration Details:**
   - Open \`config.txt\` and edit the following lines, replacing the placeholders with your actual details:

          bungie_name=YourBungieName
          bungie_api_key=YourBungieApiKey
     

   - \`YourBungieName\` should be your Bungie name in the format \`Name#1234\`.
   - \`YourBungieApiKey\` should be your Bungie.net API key.

## 🚀 Running the Script

1. **Prepare Your Environment:**
   - Ensure Destiny 2 is running and your Open Director-Roster keybinding is set to ']' (Secondary works if you want to keep your Primary binding).

2. **Run the Script:**
   - Double Click the Fireteam.py script in the contained folder
3. **Follow On-Screen Instructions:**
   - The script will immediately start running. Switch back to Destiny 2 and open the Roster wait for the script to complete the process.

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

By following these steps, you will be able to successfully run the Guardian Profile Collector script and generate combined images of Destiny 2 guardian profiles. If you encounter any issues or have any questions, please feel free to reach out for support.

---

