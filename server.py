import os
import json
import base64
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests # Need to install: pip install requests

# --- APPLICATION SETUP ---
app = Flask(__name__)
# IMPORTANT: This allows your frontend (index.html) to talk to the server
CORS(app) 

# --- DATA FILE & CONFIG FILE NAMES ---
DATA_FILE = 'system_data.json'
CONFIG_FILE = 'config.json'

# --- CONFIG RETRIEVAL (Reads from local file for persistence) ---

def load_config():
    """Loads GITHUB_PAT and other settings from config.json."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f).get('GITHUB_PAT')
        except json.JSONDecodeError:
            print(f"--- ERROR: Cannot read {CONFIG_FILE}. Check JSON format. ---")
    return None

GITHUB_PAT = load_config()

# --- DATA PERSISTENCE ---

def load_data():
    """Loads system data or creates a new structure."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Return a default structure if the file doesn't exist or is corrupt
                return {"bot_logs": [], "status_info": "Infinity Vector Persistence Layer"}
    else:
        # Create an empty structure if the file does not exist
        return {"bot_logs": [], "status_info": "Infinity Vector Persistence Layer"}

def save_data(data):
    """Saves the current system data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- HELPER FUNCTIONS ---

def log_bot_activity(bot_id, duty, status="Success", error_message=""):
    """Adds a timestamped entry to the bot_logs."""
    data = load_data()
    
    # Use the server's time for consistency
    import datetime
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    log_entry = {
        "timestamp": timestamp,
        "bot_id": bot_id,
        "duty": duty,
        "status": status,
        "error": error_message
    }
    
    # Prepend the new log entry
    data['bot_logs'].insert(0, log_entry) 
    save_data(data)

def commit_to_github(owner, repo, path, html_content, message):
    """
    Commits a new file or updates an existing one on GitHub.
    Uses the GITHUB_PAT for authentication.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_PAT}",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    content_bytes = html_content.encode('utf-8')
    encoded_content = base64.b64encode(content_bytes).decode('utf-8')

    payload = {
        "message": message,
        "content": encoded_content
    }

    # First, try to get the existing file SHA if the file exists
    sha = None
    try:
        if GITHUB_PAT:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                sha = response.json().get('sha')
                payload['sha'] = sha
    except requests.exceptions.RequestException as e:
        print(f"Error checking file existence: {e}")
        # Continue without SHA if there's an error (will create new file)

    # Now, commit the file
    response = requests.put(url, headers=headers, data=json.dumps(payload))
    return response

# --- FLASK API ROUTES ---

@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the server's current status and PAT load status."""
    # Use the server's time for consistency
    import datetime
    server_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({
        "status": "ready",
        "server_time": server_time,
        "pat_loaded": GITHUB_PAT is not None
    })

# --- NEW ROUTE TO PULL BOT LOGS (This is now fixed) ---
@app.route('/api/data', methods=['GET'])
def get_data():
    """Returns all data, including bot logs, for the frontend."""
    # load_data() ensures the system_data.json is loaded correctly
    data = load_data() 
    return jsonify(data)

@app.route('/api/bot/commit_html', methods=['POST'])
def bot_commit_html():
    """Endpoint for the bot to commit HTML content to GitHub."""
    if not GITHUB_PAT:
        log_bot_activity("Server", "Commit Attempt (Simulation)", "Error", "GITHUB_PAT not loaded.")
        return jsonify({"success": False, "error": "Server is in simulation mode (GITHUB_PAT not set)."}), 403

    try:
        data = request.json
        owner = data.get('owner')
        repo = data.get('repo')
        path = data.get('path')
        html_content = data.get('html')
        message = data.get('message', f"Bot commit: Updated {path}")
        bot_id = data.get('bot_id', 'Cleaner Bot UI')
        duty = data.get('duty', 'HTML File Update')

        if not all([owner, repo, path, html_content]):
            log_bot_activity(bot_id, duty, "Error", "Missing required parameters (owner, repo, path, html).")
            return jsonify({"success": False, "error": "Missing required parameters"}), 400

        # Perform the GitHub commit
        response = commit_to_github(owner, repo, path, html_content, message)
        
        if response.status_code in [200, 201]:
            log_bot_activity(bot_id, duty, "Success", f"File updated: {path}")
            return jsonify({"success": True, "message": f"Successfully committed {path}", "github_response": response.json()})
        else:
            error_message = response.json().get('message', response.text)
            log_bot_activity(bot_id, duty, "Error", f"GitHub API Failed: {error_message}")
            return jsonify({"success": False, "error": f"GitHub API failed: {error_message}"}), response.status_code

    except Exception as e:
        log_bot_activity("Server", "Commit Process", "Error", str(e))
        return jsonify({"success": False, "error": f"An unexpected error occurred: {str(e)}"}), 500

# --- SERVER LAUNCH ---

if __name__ == '__main__':
    if GITHUB_PAT:
        print("--- INFO: GITHUB_PAT successfully loaded for potential API calls. ---")
    else:
        print("--- WARNING: GITHUB_PAT NOT loaded. Server running in SIMULATION mode. ---")

    print("--- Starting Flask Server on Port 5000 ---")
    
    # Running on 0.0.0.0 ensures it is accessible from localhost and external devices on your network
    app.run(host='0.0.0.0', port=5000, debug=True)
