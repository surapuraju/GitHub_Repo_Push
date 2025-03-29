#-------------------------------------------------------------------------------
# Name:        GitHub_Push
# Purpose:     Push Files to GitHub Repo
#
# Author:      Raju Surapuraju
#
# Created:     28-Mar-2025
# Copyright:   (c) Raju Surapuraju 2025
# Licence:     Raju Surapuraju
#-------------------------------------------------------------------------------

import requests
import base64
import configparser
import sys
import os

# Determine Base Directory (Handles PyInstaller Paths)
def get_base_path():
    """Determine base directory whether running as script or .exe."""
    if getattr(sys, 'frozen', False):  # Running as .exe
        base_path = os.path.dirname(sys.executable)
    else:  # Running as script
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.dirname(base_path)

BASE_DIR = get_base_path()

# Paths to Config and JSON Files
CONFIG_PATH = os.path.join(BASE_DIR, "Config", "configFile.ini")

# Load Config File with Debugging
config = configparser.ConfigParser()
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"❌ Config file missing: {CONFIG_PATH}")

config.read(CONFIG_PATH, encoding="utf-8")

def get_config_value(section, key, default=None):
    """Fetch config value with debugging."""
    try:
        value = config[section][key]
        print(f"🔹 Loaded [{section}] -> {key}: {value}")
        return value
    except KeyError:
        print(f"⚠️ Warning: Missing key [{section}] -> {key}. Using default: {default}")
        return default

# Read values from config.ini
USERNAME = get_config_value("DEFAULT", "username", "default_user")
API_TOKEN = get_config_value("DEFAULT", "token", "default_pass")
BRANCH = get_config_value("DEFAULT", "Branch", "main")
REPO = get_config_value("DEFAULT", "Repo", "dummy")
FILE_PATH = get_config_value("DEFAULT", "FilePath", "dummy")

# Convert FilePath to absolute path
FILE_PATH = os.path.join(BASE_DIR, FILE_PATH)
FILE_PATH = os.path.abspath(FILE_PATH)

# Debugging: Print the resolved file path
print(f"📂 Resolved file path: {FILE_PATH}")

# Check if file exists
if not os.path.exists(FILE_PATH):
    raise FileNotFoundError(f"❌ File not found: {FILE_PATH}")

# Read the file content
with open(FILE_PATH, "rb") as file:
    content = base64.b64encode(file.read()).decode("utf-8")

# GitHub API URL for uploading file
GITHUB_API_URL = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{os.path.basename(FILE_PATH)}"

# Debugging: Print the GitHub API request details
print(f"🛠️ API URL: {GITHUB_API_URL}")
print(f"🔑 Using token: {API_TOKEN[:4]}... (hidden for security)")
print(f"📂 Target branch: {BRANCH}")
print(f"📜 File path in repo: {os.path.basename(FILE_PATH)}")

# Headers with Authorization
headers = {"Authorization": f"token {API_TOKEN}"}

# Get the file's SHA (required for updating existing files)
response = requests.get(GITHUB_API_URL, headers=headers)

if response.status_code == 200:
    sha = response.json()["sha"]
    print(f"🔍 Found existing file. SHA: {sha}")
else:
    sha = None  # New file
    print(f"🆕 New file: {os.path.basename(FILE_PATH)}")

# Commit message
commit_message = "Adding or updating file via API"

# Payload for GitHub API
payload = {
    "message": commit_message,
    "content": content,
    "branch": BRANCH
}

# Include SHA for updating an existing file
if sha:
    payload["sha"] = sha

# Make the API request
response = requests.put(GITHUB_API_URL, json=payload, headers=headers)

# Handle API Response
if response.status_code in [200, 201]:
    print("✅ File successfully committed!")
else:
    print(f"❌ Failed to commit file: {response.status_code} - {response.text}")
