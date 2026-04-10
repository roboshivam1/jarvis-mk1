from datetime import datetime
import subprocess
import difflib
import urllib.request
import urllib.parse
import json
import ssl

def get_current_time() -> str:
    """
    Returns the current local date and time.
    Use this tool whenever the user asks for the time, date, or day of the week.
    """
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")

def get_battery_status() -> str:
    """
    Checks the current battery percentage and charging status of the Mac.
    Use this tool when the user asks about the battery level, if the laptop is plugged in, or power status.
    """
    try:
        # 'pmset -g batt' is the native Mac terminal command for battery info
        result = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error checking battery: {e}"

def open_application(app_name: str) -> str:
    """
    Opens a macOS application by its name (e.g., 'Safari', 'Notes', 'Spotify').
    Use this tool when the user asks you to open, launch, or start an app.
    
    :param app_name: The name of the application to open.
    """
    try:
        # 'open -a' is the native Mac terminal command to launch apps
        subprocess.run(["open", "-a", app_name], check=True)
        return f"Successfully opened {app_name}."
    except subprocess.CalledProcessError:
        return f"Failed to open {app_name}. Please ensure the app name is correct and installed."

def set_volume(level: int) -> str:
    """
    Sets the system volume on the Mac to a specific level between 0 and 100.
    Use this tool when the user asks to change the volume, mute, or make it louder/quieter.
    
    :param level: The target volume level (0-100).
    """
    try:
        # Ensure the level stays within logical bounds
        level = max(0, min(100, int(level)))
        # 'osascript' allows us to run AppleScript from Python to control system settings
        subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
        return f"Volume successfully set to {level}%."
    except Exception as e:
        return f"Error setting volume: {e}"



def search_and_play_global_music(query: str) -> str:
    """
    Searches the global Apple Music catalog for a song or artist and plays it.
    Use this tool when the user asks to play a song that is likely NOT in their local library.
    
    :param query: The name of the song and/or artist (e.g., 'Shape of You Ed Sheeran').
    """
    try:
        # Format the search query for a URL
        safe_query = urllib.parse.quote(query)
        safe_query = safe_query.replace(' ', '+')
        # Hit the free iTunes Search API
        url = f"https://itunes.apple.com/search?term={safe_query}&limit=1&entity=song"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        context = ssl._create_unverified_context()
        
        # Pass the context into the urlopen function
        with urllib.request.urlopen(req, context=context) as response:
            data = json.loads(response.read().decode())

        if data['resultCount'] == 0:
            print(f"Could not find any global results for '{query}'.")
            return f"Could not find any global results for '{query}'."
            
        # Extract the track URL and the track name
        track_url = data['results'][0]['trackViewUrl']
        track_name = data['results'][0]['trackName']
        artist_name = data['results'][0]['artistName']
        
        # Open the URL using macOS native 'open' command. 
        # macOS is smart enough to route Apple Music URLs directly to the Music app!
        subprocess.run(["open", track_url], check=True)
        
        # We also trigger a 'play' command just in case the app opens but doesn't auto-play
        subprocess.run(["osascript", "-e", 'tell application "Music" to play'], check=False)
        
        return f"Found and playing '{track_name}' by {artist_name} from the global catalog."

    except Exception as e:
        print(f"Error searching global Apple Music: {e}")
        return f"Error searching global Apple Music: {e}"
    
def control_apple_music(command: str, track_name: str = "", playlist_name: str = "") -> str:
    """
    
    Controls the native Apple Music application on Mac for basic playback and LOCAL playlists.
    CRITICAL: ONLY use this tool for 'play', 'pause', 'next', 'previous', or 'play_playlist'.
    DO NOT use this tool to play specific tracks unless the user explicitly says "from my library".
    
    :param command: 'play', 'pause', 'next', 'previous', or 'play_playlist'.
    :param track_name: Name of the local song to play.
    :param playlist_name: Name of the playlist to play.
    """
    try:
        if command == "play":
            script = 'tell application "Music" to play'
            action_text = "Resumed playing music."
        elif command == "pause":
            script = 'tell application "Music" to pause'
            action_text = "Paused the music."
        elif command == "next":
            script = 'tell application "Music" to next track'
            action_text = "Skipped to the next track."
        elif command == "previous":
            script = 'tell application "Music" to previous track'
            action_text = "Went back to the previous track."
        elif command == "play_track" and track_name:
            script = f'tell application "Music" to play track "{track_name}"'
            action_text = f"Playing the local track '{track_name}'."
        elif command == "play_playlist" and playlist_name:
            # 1. Fetch all user playlists from Apple Music
            result = subprocess.run(["osascript", "-e", 'tell application "Music" to get name of user playlists'], capture_output=True, text=True)
            all_playlists = [p.strip() for p in result.stdout.split(',')]
            
            # 2. Use Fuzzy Matching to find the closest playlist name
            matches = difflib.get_close_matches(playlist_name, all_playlists, n=1, cutoff=0.4)
            
            if matches:
                best_match = matches[0]
                script = f'tell application "Music" to play playlist "{best_match}"'
                action_text = f"Playing the playlist '{best_match}'."
            else:
                return f"Could not find any playlist matching '{playlist_name}'."
        else:
            return "Error: Invalid command."
            
        subprocess.run(["osascript", "-e", script], check=True)
        return action_text
    
    except Exception as e:
        return f"Error controlling Apple Music: {e}"

# We create a dictionary to easily map the function name (string) to the actual Python function
AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "get_battery_status": get_battery_status,
    "open_application": open_application,
    "set_volume": set_volume,
    "control_apple_music": control_apple_music,
    "search_and_play_global_music": search_and_play_global_music
}