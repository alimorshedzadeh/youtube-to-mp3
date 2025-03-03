import os
import json
import sqlite3
import shutil
import base64
from pathlib import Path

def get_chrome_cookies():
    """Extract cookies from Chrome browser."""
    try:
        # Get Chrome cookies path
        chrome_path = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Cookies')
        if not os.path.exists(chrome_path):
            print("Chrome cookies not found")
            return False

        # Create a copy of the cookies file
        temp_path = 'chrome_cookies_temp'
        shutil.copy2(chrome_path, temp_path)

        # Connect to the temporary database
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        # Extract YouTube cookies
        cursor.execute("""
            SELECT host_key, name, value, path, expires_utc 
            FROM cookies 
            WHERE host_key LIKE '%youtube.com%'
        """)

        # Create a secure cookies file
        cookies_data = []
        for row in cursor.fetchall():
            host, name, value, path, expires = row
            cookies_data.append({
                'host': host,
                'name': name,
                'value': value,
                'path': path,
                'expires': expires
            })

        # Save cookies in a secure format
        with open('secure_cookies.json', 'w') as f:
            json.dump(cookies_data, f, indent=2)

        conn.close()
        os.remove(temp_path)
        print("Chrome cookies extracted successfully")
        return True
    except Exception as e:
        print(f"Error extracting Chrome cookies: {e}")
        return False

def get_firefox_cookies():
    """Extract cookies from Firefox browser."""
    try:
        # Get Firefox cookies path
        firefox_path = os.path.expanduser('~/Library/Application Support/Firefox/Profiles')
        if not os.path.exists(firefox_path):
            print("Firefox cookies not found")
            return False

        # Find the default profile
        profiles = [d for d in os.listdir(firefox_path) if d.endswith('.default-release')]
        if not profiles:
            print("No Firefox default profile found")
            return False

        profile_path = os.path.join(firefox_path, profiles[0])
        cookies_path = os.path.join(profile_path, 'cookies.sqlite')

        if not os.path.exists(cookies_path):
            print("Firefox cookies database not found")
            return False

        # Create a copy of the cookies file
        temp_path = 'firefox_cookies_temp'
        shutil.copy2(cookies_path, temp_path)

        # Connect to the temporary database
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        # Extract YouTube cookies
        cursor.execute("""
            SELECT host, name, value, path, expiry 
            FROM moz_cookies 
            WHERE host LIKE '%youtube.com%'
        """)

        # Create a secure cookies file
        cookies_data = []
        for row in cursor.fetchall():
            host, name, value, path, expiry = row
            cookies_data.append({
                'host': host,
                'name': name,
                'value': value,
                'path': path,
                'expires': expiry
            })

        # Save cookies in a secure format
        with open('secure_cookies.json', 'w') as f:
            json.dump(cookies_data, f, indent=2)

        conn.close()
        os.remove(temp_path)
        print("Firefox cookies extracted successfully")
        return True
    except Exception as e:
        print(f"Error extracting Firefox cookies: {e}")
        return False

def main():
    """Main function to extract cookies from browsers."""
    print("Starting cookie extraction...")
    
    # Try Chrome first
    if get_chrome_cookies():
        print("Using Chrome cookies")
    # If Chrome fails, try Firefox
    elif get_firefox_cookies():
        print("Using Firefox cookies")
    else:
        print("Failed to extract cookies from both browsers")
        return

    print("Cookie extraction complete. Check secure_cookies.json file.")

if __name__ == '__main__':
    main() 