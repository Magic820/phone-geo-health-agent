#!/usr/bin/env python3
"""
doubao-chat: Simulate real user chat with Doubao (doubao.com).

Supports two modes:
  1. Chrome CDP mode: Connect to an already-logged-in Chrome browser
  2. Standalone mode (recommended): Use Playwright's built-in Chromium with cookie persistence

Supports single or multiple questions in one session.

Usage:
    python chat.py "你的问题"
    python chat.py "Q1" "Q2" "Q3"
    python chat.py --questions-file questions.txt
    python chat.py "你的问题" --standalone
    python chat.py "你的问题" --timeout=120
    python chat.py "你的问题" --new-thread
    python chat.py "你的问题" --screenshot-dir=./debug

Returns JSON:
    Single:  {"success": true, "question": "...", "answer": "...", "references": [...], ...}
    Batch:   {"success": true, "results": [{"question": "...", "answer": "...", "references": [...]}, ...]}
    Error:   {"success": false, "error": "ERROR_CODE", "message": "..."}
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "PLAYWRIGHT_NOT_INSTALLED",
        "message": "Playwright not installed. Run: pip install playwright && playwright install chromium"
    }))
    sys.exit(1)


# ---------------------------------------------------------------------------
# Selector strategies (ordered by priority)
# ---------------------------------------------------------------------------

INPUT_SELECTORS = [
    'textarea[class*="input"]',
    'textarea[class*="chat"]',
    'textarea[class*="editor"]',
    'textarea[placeholder]',
    'div[contenteditable="true"][class*="input"]',
    'div[contenteditable="true"][class*="editor"]',
    'div[contenteditable="true"][class*="chat"]',
    'div[contenteditable="true"]',
    'textarea',
]

SEND_SELECTORS = [
    'button[class*="send"]',
    'button[aria-label*="发送"]',
    'button[aria-label*="Send"]',
    'button[data-testid*="send"]',
    'button:has(svg)',
]


# ---------------------------------------------------------------------------
# Cookie / State persistence
# ---------------------------------------------------------------------------

def get_cookie_storage_dir():
    """Get the directory for storing Doubao browser state."""
    base = Path.home() / ".doubao-chat"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_state_file_path():
    return get_cookie_storage_dir() / "state.json"


def save_browser_state(context, verbose=False):
    """Save browser state (cookies, localStorage) for future sessions."""
    state_file = get_state_file_path()
    try:
        context.storage_state(path=str(state_file))
        if verbose:
            print(f"[DEBUG] Saved browser state to {state_file}", file=sys.stderr)
    except Exception as e:
        if verbose:
            print(f"[DEBUG] Failed to save browser state: {e}", file=sys.stderr)


def connect_standalone(p, headless=False, verbose=False):
    """Launch Playwright's built-in Chromium with cookie persistence.

    Key fix: ALWAYS try to load state.json if it exists, even in headless mode.
    """
    state_file = get_state_file_path()

    browser = p.chromium.launch(
        headless=headless,
        args=["--disable-blink-features=AutomationControlled"],
    )

    context = None
    if state_file.exists():
        try:
            context = browser.new_context(storage_state=str(state_file))
            if verbose:
                print(f"[DEBUG] Loaded saved browser state from {state_file}", file=sys.stderr)
        except Exception as e:
            if verbose:
                print(f"[DEBUG] Failed to load state.json (will create fresh context): {e}",
                      file=sys.stderr)
            context = None

    if context is None:
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    page = context.new_page()
    return browser, context, page


# ---------------------------------------------------------------------------
# DOM helpers
# ---------------------------------------------------------------------------

def find_input(page):
    """Find the chat input element using multiple strategies."""
    for selector in INPUT_SELECTORS:
        try:
            loc = page.locator(selector).first
            if loc.is_visible(timeout=300):
                return loc, selector
        except Exception:
            continue

    for keyword in ["输入", "问", "聊天", "Ask", "Chat", "Message"]:
        try:
            loc = page.locator(f'[placeholder*="{keyword}"]').first
            if loc.is_visible(timeout=300):
                return loc, f'[placeholder*="{keyword}"]'
        except Exception:
            continue

    try:
        loc = page.get_by_role("textbox").first
        if loc.is_visible(timeout=500):
            return loc, "role=textbox"
    except Exception:
        pass

    return None, None


def find_send_button(page):
    """Find the send button near the input area."""
    for selector in SEND_SELECTORS:
        try:
            loc = page.locator(selector).last
            if loc.is_visible(timeout=200):
                return loc, selector
        except Exception:
            continue

    try:
        buttons = page.locator("button").all()
        for btn in reversed(buttons):
            try:
                if btn.is_visible(timeout=100):
                    text = btn.inner_text()
                    aria = btn.get_attribute("aria-label") or ""
                    if any(kw in (text + aria) for kw in ["发送", "Send", "submit"]):
                        return btn, "button(text/aria contains send)"
            except Exception:
                continue
    except Exception:
        pass

    return None, None


def check_login(page, standalone=False, wait_for_login=True, verbose=False):
    """Check if the user is logged in on Doubao.

    Returns True if logged in. In standalone mode, will wait for user to login.
    """
    try:
        login_indicators = [
            'button:has-text("登录")',
            'a:has-text("登录")',
            'div:has-text("请先登录")',
            'button:has-text("Log in")',
            '[class*="semi-modal"] button:has-text("登录")',
        ]
        has_login_button = False
        for indicator in login_indicators:
            try:
                if page.locator(indicator).count() > 0:
                    has_login_button = True
                    break
            except Exception:
                continue

        inp, _ = find_input(page)

        if not has_login_button and inp:
            return True

        if has_login_button:
            if standalone and wait_for_login:
                print("[INFO] ⚠️  豆包需要登录。请在弹出的浏览器窗口中扫码或输入手机号登录...",
                      file=sys.stderr)
                for _ in range(150):
                    time.sleep(2)
                    has_login_now = False
                    for indicator in login_indicators:
                        try:
                            if page.locator(indicator).count() > 0:
                                has_login_now = True
                                break
                        except Exception:
                            continue
                    if not has_login_now:
                        inp2, _ = find_input(page)
                        if inp2:
                            print("[INFO] ✅ 登录成功！", file=sys.stderr)
                            return True
                return False
            return False

        if inp:
            return True

        if standalone and wait_for_login:
            print("[INFO] Waiting for Doubao page to load...", file=sys.stderr)
            for _ in range(30):
                time.sleep(2)
                inp2, _ = find_input(page)
                if inp2:
                    return True
        return False
    except Exception:
        return False


def dismiss_modals(page, verbose=False):
    """Dismiss any blocking modals on the page."""
    modal_close_selectors = [
        'button[class*="close"]',
        'div[class*="modal"] button[class*="close"]',
        'div[class*="modal"] div[class*="close"]',
        'div[class*="modal"] svg',
        '[class*="semi-modal"] button',
        '[class*="semi-modal"] div[class*="close"]',
        '[class*="semi-modal"] svg',
        '.semi-modal-wrap button',
        'div[role="none"] button',
        'div[class*="modal"] [class*="icon"]',
    ]
    for sel in modal_close_selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=300):
                loc.click(timeout=2000)
                if verbose:
                    print(f"[DEBUG] Dismissed modal with: {sel}", file=sys.stderr)
                time.sleep(0.5)
                return True
        except Exception:
            continue
    return False


def wait_for_response(page, timeout=120, poll_interval=1, verbose=False):
    """Wait for the AI response to complete generating.

    Key insight: Doubao's sidebar has persistent [class*="skeleton"] elements
    that NEVER go away, so we must NOT treat them as streaming indicators.
    Instead, we check streaming ONLY within the response markdown area,
    and use markdown content stability as the primary completion signal.
    """
    start_time = time.time()
    last_content_length = 0
    stable_count = 0
    required_stable_checks = 3

    time.sleep(3)  # Minimum wait for response to start

    while time.time() - start_time < timeout:
        try:
            # --- Streaming check: ONLY within response area ---
            is_streaming = False

            # Find the response container (markdown area)
            response_el = None
            for sel in ["div[class*='markdown-body']", "div[class*='markdown']"]:
                try:
                    els = page.locator(sel).all()
                    if els:
                        response_el = els[-1]
                        break
                except Exception:
                    continue

            if response_el:
                # Check streaming indicators WITHIN the response only
                for sel in [
                    ':scope div[class*="typing"]',
                    ':scope div[class*="loading"]',
                    ':scope div[class*="streaming"]',
                    ':scope span[class*="cursor"]',
                    ':scope div[class*="generating"]',
                ]:
                    try:
                        if response_el.locator(sel).count() > 0:
                            is_streaming = True
                            break
                    except Exception:
                        continue
            else:
                # Fallback: global check (exclude skeleton!)
                for sel in [
                    'div[class*="typing"]',
                    'div[class*="streaming"]',
                    'span[class*="cursor"]',
                    'div[class*="generating"]',
                ]:
                    try:
                        if page.locator(sel).count() > 0:
                            is_streaming = True
                            break
                    except Exception:
                        continue

            # --- Content length: prioritize markdown area ---
            current_length = 0
            for sel in ["div[class*='markdown-body']", "div[class*='markdown']"]:
                try:
                    msgs = page.locator(sel).all()
                    if msgs:
                        current_length = len(msgs[-1].inner_text() or "")
                        if current_length > 0:
                            break
                except Exception:
                    continue

            if current_length == 0:
                for sel in ["div[class*='message']", "div[class*='msg']"]:
                    try:
                        msgs = page.locator(sel).all()
                        if msgs:
                            current_length = len(msgs[-1].inner_text() or "")
                            if current_length > 0:
                                break
                    except Exception:
                        continue

            # --- Stability check ---
            if current_length > 0 and current_length == last_content_length:
                stable_count += 1
            else:
                stable_count = 0

            last_content_length = current_length

            if verbose and stable_count == 0 and current_length > 0:
                print(f"[DEBUG] Response length: {current_length}, streaming: {is_streaming}",
                      file=sys.stderr)

            # Complete: no streaming + stable content
            if not is_streaming and stable_count >= required_stable_checks and current_length > 0:
                if verbose:
                    print(f"[DEBUG] Response complete! Length: {current_length}", file=sys.stderr)
                return True

            # Early exit: long + stable
            if current_length > 100 and stable_count >= 2 and not is_streaming:
                if verbose:
                    print(f"[DEBUG] Response complete (early)! Length: {current_length}",
                          file=sys.stderr)
                return True

            time.sleep(poll_interval)
        except Exception:
            time.sleep(poll_interval)
            continue

    return False


def extract_response_with_references(page):
    """Extract the last AI response text AND reference links from the page.

    Returns (answer_text, extraction_method, references_list).
    references_list contains dicts: {text, url, index}
    """
    references = []

    # --- Extract references from the response ---
    # Doubao uses superscript numbers linking to sources
    ref_data = page.evaluate('''() => {
        const refs = [];
        // Find all <a> tags in the last response area
        const responseSelectors = [
            'div[class*="markdown-body"]',
            'div[class*="markdown"]',
            'div[class*="assistant"]',
            'div[class*="bot"]',
            'div[class*="answer"]',
            'div[class*="reply"]',
        ];

        let responseEl = null;
        for (const sel of responseSelectors) {
            const els = document.querySelectorAll(sel);
            if (els.length > 0) {
                responseEl = els[els.length - 1];
                break;
            }
        }

        if (!responseEl) {
            // Fallback: find the main content area
            const main = document.querySelector('main');
            responseEl = main || document.body;
        }

        // Extract all links with meaningful href
        const links = responseEl.querySelectorAll('a[href]');
        let refIndex = 1;
        for (const link of links) {
            const href = link.getAttribute('href') || '';
            const text = (link.innerText || '').trim();
            // Skip empty, javascript:, and # links
            if (href && !href.startsWith('javascript') && href !== '#' && href.length > 2) {
                refs.push({
                    index: refIndex++,
                    text: text || href,
                    url: href
                });
            }
        }

        // Also look for superscript reference markers (豆包 uses [1], [2] style)
        const sups = responseEl.querySelectorAll('sup, span[class*="ref"], span[class*="cite"], a[class*="ref"]');
        for (const sup of sups) {
            const text = (sup.innerText || '').trim();
            const href = sup.getAttribute('href') || sup.closest('a')?.getAttribute('href') || '';
            if (text && (href || text.match(/\\[\\d+\\]/))) {
                // Avoid duplicates
                if (!refs.find(r => r.text === text && r.url === href)) {
                    refs.push({
                        index: refIndex++,
                        text: text,
                        url: href || ''
                    });
                }
            }
        }

        return refs;
    }''')

    if ref_data:
        references = ref_data

    # --- Extract response text ---
    response_patterns = [
        "div[class*='markdown-body']",
        "div[class*='markdown']",
        "div[class*='bot']",
        "div[class*='assistant']",
        "div[class*='answer']",
        "div[class*='reply']",
        "div[class*='ai-message']",
        "div[data-role='assistant']",
        "div[class*='message-content']",
    ]

    for pattern in response_patterns:
        try:
            elements = page.locator(pattern).all()
            if elements:
                last_el = elements[-1]
                if last_el.is_visible(timeout=500):
                    text = last_el.inner_text()
                    if text and len(text.strip()) > 0:
                        return text.strip(), pattern, references
        except Exception:
            continue

    # Fallback: last message container
    try:
        messages = page.locator(
            "div[class*='message'], div[class*='msg'], div[class*='chat-item']"
        ).all()
        if len(messages) >= 2:
            last_msg = messages[-1]
            text = last_msg.inner_text()
            if text and len(text.strip()) > 0:
                return text.strip(), "last-message-container", references
    except Exception:
        pass

    # Final fallback: chat area
    try:
        chat_area = page.locator(
            "div[class*='chat-list'], div[class*='conversation'], div[class*='dialogue'], main"
        ).first
        all_text = chat_area.inner_text()
        if all_text:
            return all_text.strip(), "chat-area-fallback", references
    except Exception:
        pass

    return None, None, references


def take_screenshot(page, screenshot_dir, name="debug"):
    """Take a screenshot for debugging."""
    if not screenshot_dir:
        return None
    try:
        os.makedirs(screenshot_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(screenshot_dir, f"{name}_{ts}.png")
        page.screenshot(path=path, full_page=False)
        return path
    except Exception:
        return None


def _make_error(error, message, **extra):
    """Build a standardized error result dict."""
    result = {"success": False, "error": error, "message": message}
    result.update(extra)
    return result


# ---------------------------------------------------------------------------
# Core: send one question and get response
# ---------------------------------------------------------------------------

def _send_and_wait(page, question, timeout, screenshot_dir, verbose, send_selector_ref=None):
    """Send a single question to Doubao and wait for the response.

    Returns a result dict with answer + references, or an error dict.
    """
    # ---- Find input ----
    input_el, input_selector = find_input(page)
    if not input_el:
        take_screenshot(page, screenshot_dir, "input-not-found")
        return _make_error("INPUT_NOT_FOUND", "Cannot find the chat input box.")

    if verbose:
        print(f"[DEBUG] Found input: {input_selector}", file=sys.stderr)

    # ---- Type question ----
    try:
        input_el.click()
        time.sleep(0.3)
        input_el.fill("")
        time.sleep(0.2)
        input_el.fill(question)
        time.sleep(0.3)
    except Exception:
        try:
            input_el.click()
            time.sleep(0.2)
            page.keyboard.press("Control+a")
            page.keyboard.press("Backspace")
            time.sleep(0.2)
            input_el.type(question, delay=30)
            time.sleep(0.3)
        except Exception as e:
            take_screenshot(page, screenshot_dir, "input-failed")
            return _make_error("INPUT_FAILED", f"Failed to type question: {str(e)}")

    # ---- Send ----
    send_btn, send_selector = find_send_button(page)
    if send_btn:
        try:
            send_btn.click()
            if verbose:
                print(f"[DEBUG] Clicked send: {send_selector}", file=sys.stderr)
        except Exception:
            page.keyboard.press("Enter")
            send_selector = "Enter(fallback)"
            if verbose:
                print("[DEBUG] Send click failed, used Enter", file=sys.stderr)
    else:
        page.keyboard.press("Enter")
        send_selector = "Enter"
        if verbose:
            print("[DEBUG] No send button, used Enter", file=sys.stderr)

    # Store for caller
    if send_selector_ref is not None:
        send_selector_ref["value"] = send_selector

    time.sleep(2)

    # ---- Wait for response ----
    response_received = wait_for_response(page, timeout=timeout, verbose=verbose)

    if not response_received:
        take_screenshot(page, screenshot_dir, "response-timeout")
        answer, method, refs = extract_response_with_references(page)
        return _make_error(
            "RESPONSE_TIMEOUT",
            f"Timed out waiting for response after {timeout}s.",
            partial_answer=answer,
            references=refs,
            meta={"extractionMethod": method, "pageUrl": page.url}
        )

    # ---- Extract response + references ----
    answer, extraction_method, references = extract_response_with_references(page)
    if not answer:
        take_screenshot(page, screenshot_dir, "extraction-failed")
        return _make_error(
            "RESPONSE_EXTRACTION_FAILED",
            "Response completed but could not extract text.",
            references=references,
            meta={"pageUrl": page.url}
        )

    return {
        "success": True,
        "answer": answer,
        "references": references if references else [],
        "meta": {
            "extractionMethod": extraction_method,
        }
    }


# ---------------------------------------------------------------------------
# Main chat function (supports single + batch)
# ---------------------------------------------------------------------------

def chat_with_doubao(questions, cdp_url="http://127.0.0.1:9222", timeout=120,
                     new_thread=False, screenshot_dir=None, verbose=False,
                     standalone=False, headless=False):
    """Send one or more questions to Doubao and get responses.

    Args:
        questions: str or list[str] — one or more questions to ask.

    Returns:
        Single question: {"success": true, "question": "...", "answer": "...", "references": [...], ...}
        Multiple:       {"success": true, "results": [{...}, ...], ...}
    """
    is_batch = isinstance(questions, list) and len(questions) > 1
    if isinstance(questions, str):
        questions = [questions]

    with sync_playwright() as p:
        browser = None
        context = None
        page = None
        own_browser = False

        try:
            # ---- Connect to browser ----
            if standalone:
                try:
                    browser, context, page = connect_standalone(p, headless=headless, verbose=verbose)
                    own_browser = True
                except Exception as e:
                    return _make_error("STANDALONE_LAUNCH_FAILED",
                                       f"Failed to launch standalone browser: {str(e)}")
            else:
                try:
                    browser = p.chromium.connect_over_cdp(cdp_url)
                except Exception as e:
                    return _make_error(
                        "CDP_CONNECTION_FAILED",
                        f"Cannot connect to Chrome CDP at {cdp_url}. "
                        f"Ensure Chrome is running with --remote-debugging-port=9222. "
                        f"Or use --standalone mode. Detail: {str(e)}"
                    )

                try:
                    contexts = browser.contexts
                    if contexts:
                        context = contexts[0]
                        pages = context.pages
                        page = pages[0] if pages else context.new_page()
                    else:
                        context = browser.new_context()
                        page = context.new_page()
                except Exception as e:
                    return _make_error("PAGE_CREATION_FAILED",
                                       f"Failed to create/access page: {str(e)}")

            # ---- Navigate to Doubao chat ----
            try:
                target_url = "https://www.doubao.com/chat/"
                if "doubao.com" not in (page.url or "") or new_thread:
                    page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
                try:
                    page.wait_for_load_state("networkidle", timeout=20000)
                except Exception:
                    if verbose:
                        print("[DEBUG] networkidle timed out, continuing anyway...",
                              file=sys.stderr)
                    time.sleep(3)
            except Exception as e:
                take_screenshot(page, screenshot_dir, "nav-failed")
                return _make_error("NAVIGATION_FAILED",
                                   f"Failed to navigate to doubao.com/chat: {str(e)}")

            # ---- Check login ----
            if not check_login(page, standalone=standalone, wait_for_login=standalone,
                               verbose=verbose):
                take_screenshot(page, screenshot_dir, "not-logged-in")
                if standalone and context:
                    save_browser_state(context, verbose=verbose)
                return _make_error(
                    "NOT_LOGGED_IN",
                    "Not logged in to Doubao. "
                    + ("Please log in via Chrome first, then retry." if not standalone
                       else "Login wait timed out. Please try again.")
                )

            # Save state immediately after login confirmed (so we don't lose it)
            if standalone and context:
                save_browser_state(context, verbose=verbose)

            # ---- Dismiss modals ----
            dismiss_modals(page, verbose=verbose)

            # ---- Send questions sequentially ----
            results = []
            for i, question in enumerate(questions):
                if verbose:
                    print(f"[DEBUG] Sending question {i+1}/{len(questions)}: {question[:50]}...",
                          file=sys.stderr)

                # For 2nd+ question, wait a moment and dismiss any new modals
                if i > 0:
                    time.sleep(1)
                    dismiss_modals(page, verbose=verbose)

                send_info = {}
                result = _send_and_wait(page, question, timeout, screenshot_dir, verbose,
                                        send_selector_ref=send_info)

                # Enrich result with question + metadata
                if result.get("success"):
                    result["question"] = question
                    result["timestamp"] = datetime.now(timezone.utc).isoformat()
                    result["meta"].update({
                        "pageUrl": page.url,
                        "mode": "standalone" if standalone else "cdp",
                        "sendMethod": send_info.get("value", "unknown"),
                    })
                else:
                    result["question"] = question

                results.append(result)

                # If a question failed, still continue with remaining questions
                if not result.get("success"):
                    if verbose:
                        print(f"[DEBUG] Question {i+1} failed: {result.get('error')}",
                              file=sys.stderr)

                # Save state after each successful question
                if standalone and context and result.get("success"):
                    save_browser_state(context, verbose=verbose)

            # ---- Return results ----
            if is_batch:
                # Batch mode: return array of results
                all_success = all(r.get("success") for r in results)
                return {
                    "success": all_success,
                    "results": results,
                    "totalQuestions": len(questions),
                    "successCount": sum(1 for r in results if r.get("success")),
                    "failCount": sum(1 for r in results if not r.get("success")),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "meta": {
                        "mode": "standalone" if standalone else "cdp",
                    }
                }
            else:
                # Single question: return flat result
                return results[0]

        except Exception as e:
            return _make_error("UNEXPECTED_ERROR", f"Unexpected error: {str(e)}")
        finally:
            if own_browser and browser:
                try:
                    # Save state one final time before closing
                    if standalone and context:
                        save_browser_state(context, verbose=verbose)
                    browser.close()
                except Exception:
                    pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Chat with Doubao via Playwright (CDP or Standalone mode)"
    )
    parser.add_argument("questions", nargs="*", default=[], help="Question(s) to ask Doubao (optional if --questions-file is used)")
    parser.add_argument(
        "--questions-file", "-f",
        help="File with one question per line (alternative to positional args)"
    )
    parser.add_argument(
        "--cdp-url",
        default=os.environ.get("DOUBAO_CDP_URL", "http://127.0.0.1:9222"),
        help="Chrome DevTools Protocol URL (default: http://127.0.0.1:9222)"
    )
    parser.add_argument(
        "--timeout", type=int,
        default=int(os.environ.get("DOUBAO_CHAT_TIMEOUT", "120")),
        help="Maximum wait time per response in seconds (default: 120)"
    )
    parser.add_argument(
        "--new-thread", action="store_true",
        help="Start a new chat thread instead of continuing the current one"
    )
    parser.add_argument(
        "--standalone", action="store_true",
        default=os.environ.get("DOUBAO_STANDALONE", "") == "1",
        help="Use Playwright's built-in Chromium instead of Chrome CDP"
    )
    parser.add_argument(
        "--headless", action="store_true",
        default=os.environ.get("DOUBAO_HEADLESS", "") == "1",
        help="Run browser in headless mode (standalone only, login required first)"
    )
    parser.add_argument(
        "--screenshot-dir",
        default=os.environ.get("DOUBAO_SCREENSHOT_DIR", ""),
        help="Directory to save debug screenshots"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        default=os.environ.get("DOUBAO_VERBOSE", "") == "1",
        help="Enable verbose debug output"
    )

    args = parser.parse_args()

    # Collect questions from args and/or file
    question_list = list(args.questions)
    if args.questions_file:
        try:
            with open(args.questions_file, "r", encoding="utf-8") as f:
                file_questions = [line.strip() for line in f if line.strip()]
            question_list = file_questions + question_list
        except FileNotFoundError:
            print(json.dumps(_make_error("FILE_NOT_FOUND", f"Questions file not found: {args.questions_file}"), ensure_ascii=False))
            sys.exit(1)
        except Exception as e:
            print(json.dumps(_make_error("FILE_READ_ERROR", f"Failed to read questions file: {str(e)}"), ensure_ascii=False))
            sys.exit(1)

    # Filter out placeholder values (common when using --questions-file)
    question_list = [q for q in question_list if q and q.lower() not in ("placeholder", "null", "none", "")]

    if not question_list:
        print(json.dumps(_make_error("NO_QUESTIONS", "No questions provided. Use positional arguments or --questions-file."), ensure_ascii=False))
        sys.exit(1)

    result = chat_with_doubao(
        questions=question_list,
        cdp_url=args.cdp_url,
        timeout=args.timeout,
        new_thread=args.new_thread,
        screenshot_dir=args.screenshot_dir or None,
        verbose=args.verbose,
        standalone=args.standalone,
        headless=args.headless,
    )

    # Handle Windows encoding issues
    try:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except UnicodeEncodeError:
        # Fallback for Windows terminals with GBK encoding
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
