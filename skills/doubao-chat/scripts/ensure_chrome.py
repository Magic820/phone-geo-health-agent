#!/usr/bin/env python3
"""
ensure_chrome: Check/start Chrome with remote debugging and verify Doubao login.

Usage:
    python ensure_chrome.py
    python ensure_chrome.py --cdp-url=http://127.0.0.1:9222
    python ensure_chrome.py --start-only

Returns JSON:
    {"ready": true, "chrome_running": true, "doubao_logged_in": true}
    {"ready": false, "chrome_running": false, "doubao_logged_in": false, "message": "..."}
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request
import urllib.error


def find_chrome_path():
    """Find the Chrome executable path on the current system."""
    system = platform.system()

    if system == "Windows":
        possible_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LocalAppData", ""), "Google", "Chrome", "Application", "chrome.exe"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        # Also check Windows registry
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
            reg_path, _ = winreg.QueryValueEx(key, "")
            if reg_path and os.path.isfile(reg_path):
                return reg_path
        except Exception:
            pass
    elif system == "Darwin":
        possible_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
    else:  # Linux
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]

    for path in possible_paths:
        if path and os.path.isfile(path):
            return path

    return None


def get_chrome_user_data_dir():
    """Get the default Chrome user data directory."""
    system = platform.system()

    if system == "Windows":
        local_app_data = os.environ.get("LocalAppData", "")
        if local_app_data and os.path.isdir(os.path.join(local_app_data, "Google", "Chrome", "User Data")):
            return os.path.join(local_app_data, "Google", "Chrome", "User Data")
        # Fallback to common paths
        common_paths = [
            r"C:\Users\{}\AppData\Local\Google\Chrome\User Data".format(os.environ.get("USERNAME", "")),
        ]
        for p in common_paths:
            if os.path.isdir(p):
                return p
        return r"C:\Users\{}\AppData\Local\Google\Chrome\User Data".format(os.environ.get("USERNAME", ""))
    elif system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Google/Chrome")
    else:
        return os.path.expanduser("~/.config/google-chrome")


def check_cdp_available(cdp_url):
    """Check if Chrome DevTools Protocol is accessible."""
    try:
        version_url = f"{cdp_url}/json/version"
        req = urllib.request.Request(version_url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return True, data
    except Exception:
        return False, None


def start_chrome_debug(cdp_port=9222, user_data_dir=None):
    """Start Chrome with remote debugging enabled."""
    chrome_path = find_chrome_path()
    if not chrome_path:
        return False, "Chrome not found. Please install Google Chrome."

    if not user_data_dir:
        user_data_dir = get_chrome_user_data_dir()

    cmd = [
        chrome_path,
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={user_data_dir}",
        "--profile-directory=Default",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    try:
        if platform.system() == "Windows":
            # Use DETACHED_PROCESS on Windows to avoid inheriting console
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

        # Wait for Chrome to start
        time.sleep(3)
        return True, "Chrome started with remote debugging"
    except Exception as e:
        return False, f"Failed to start Chrome: {str(e)}"


def check_doubao_login(cdp_url):
    """Check if Doubao is logged in by connecting via Playwright."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(cdp_url)
            contexts = browser.contexts
            if not contexts:
                return False, "No browser context found"

            context = contexts[0]
            pages = context.pages

            # Find or create a page on doubao.com
            doubao_page = None
            for pg in pages:
                if "doubao.com" in (pg.url or ""):
                    doubao_page = pg
                    break

            if not doubao_page:
                doubao_page = context.new_page()
                doubao_page.goto("https://www.doubao.com/chat/",
                                wait_until="domcontentloaded", timeout=20000)
                doubao_page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(2)

            # Check for login indicators
            # If we can find a chat input, user is logged in
            login_indicators = [
                'textarea',
                'div[contenteditable="true"]',
                '[placeholder*="输入"]',
                '[placeholder*="问"]',
            ]

            for selector in login_indicators:
                try:
                    if doubao_page.locator(selector).count() > 0:
                        return True, "Doubao is logged in"
                except Exception:
                    continue

            # Check for login button (means NOT logged in)
            logout_indicators = [
                'button:has-text("登录")',
                'a:has-text("登录")',
            ]

            for selector in logout_indicators:
                try:
                    if doubao_page.locator(selector).count() > 0:
                        return False, "Not logged in - login button found"
                except Exception:
                    continue

            # Uncertain state
            return False, "Cannot determine login status - please check manually"

    except ImportError:
        return False, "Playwright not installed"
    except Exception as e:
        return False, f"Error checking login: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description="Ensure Chrome is running with debugging and Doubao is logged in"
    )
    parser.add_argument(
        "--cdp-url",
        default=os.environ.get("DOUBAO_CDP_URL", "http://127.0.0.1:9222"),
        help="Chrome CDP URL (default: http://127.0.0.1:9222)"
    )
    parser.add_argument(
        "--start-only",
        action="store_true",
        help="Only start Chrome, don't check Doubao login"
    )
    parser.add_argument(
        "--user-data-dir",
        default=None,
        help="Custom Chrome user data directory"
    )

    args = parser.parse_args()
    cdp_port = int(args.cdp_url.split(":")[-1].rstrip("/"))

    result = {
        "ready": False,
        "chrome_running": False,
        "doubao_logged_in": False,
        "message": ""
    }

    # Step 1: Check if Chrome CDP is available
    cdp_ok, version_data = check_cdp_available(args.cdp_url)

    if cdp_ok:
        result["chrome_running"] = True
        result["message"] = "Chrome CDP is available"
        if version_data:
            result["chrome_version"] = version_data.get("Browser", "unknown")
    else:
        # Step 2: Try to start Chrome
        started, msg = start_chrome_debug(cdp_port, args.user_data_dir)

        if not started:
            result["message"] = msg
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)

        # Wait and verify CDP is now available
        for _ in range(10):
            time.sleep(1)
            cdp_ok, _ = check_cdp_available(args.cdp_url)
            if cdp_ok:
                break

        if cdp_ok:
            result["chrome_running"] = True
            result["message"] = "Chrome started successfully"
        else:
            result["message"] = "Chrome was started but CDP is not responding. " \
                                "A Chrome instance may already be running. " \
                                "Close all Chrome windows and try again."
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)

    if args.start_only:
        result["ready"] = True
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # Step 3: Check Doubao login
    logged_in, login_msg = check_doubao_login(args.cdp_url)
    result["doubao_logged_in"] = logged_in

    if logged_in:
        result["ready"] = True
        result["message"] = "Doubao is logged in and ready"
    else:
        result["message"] = f"Doubao is not logged in: {login_msg}. " \
                            f"Please log in to Doubao in the Chrome browser, then retry."

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result["ready"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
