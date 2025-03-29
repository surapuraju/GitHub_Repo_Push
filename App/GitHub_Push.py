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
#GITHUB_API_URL = get_config_value("DEFAULT", "url")
USERNAME = get_config_value("DEFAULT", "username", "default_user")
API_TOKEN = get_config_value("DEFAULT", "token", "default_pass")
BRANCH = get_config_value("DEFAULT", "Branch", "main")
REPO = get_config_value("DEFAULT", "Repo", "dummy")
FILE_PATH = get_config_value("DEFAULT", "FilePath", "dummy")
# Ensure FILE_PATH is relative to GitHub_Repo_Push, not App
FILE_PATH = os.path.join(BASE_DIR, FILE_PATH)
FILE_PATH = os.path.abspath(FILE_PATH)  # Convert to absolute path

# Read the file content
with open(FILE_PATH, "rb") as file:
    content = base64.b64encode(file.read()).decode("utf-8")

GITHUB_API_URL = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{FILE_PATH}"

# Get the file's SHA (required for updating existing files)
response = requests.get(GITHUB_API_URL, auth=(USERNAME, API_TOKEN))

if response.status_code == 200:
    sha = response.json()["sha"]
else:
    sha = None  # New file

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
response = requests.put(GITHUB_API_URL, json=payload, auth=(USERNAME, API_TOKEN))

if response.status_code in [200, 201]:
    print("✅ File successfully committed!")
else:
    print(f"❌ Failed to commit file: {response.status_code} - {response.text}")
