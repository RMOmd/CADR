import time
import requests
from playwright.sync_api import sync_playwright

def wait_for_server(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Server is up at {url}")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    print(f"Timeout waiting for server at {url}")
    return False

def take_screenshot():
    url = "http://127.0.0.1:8010"
    if not wait_for_server(url):
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        
        print("Navigating to page...")
        page.goto(url, wait_until="networkidle")
        
        # Give it a second to render any client-side JS charts/data
        page.wait_for_timeout(2000)
        
        print("Taking screenshot...")
        page.screenshot(path="screenshot.png")
        print("Screenshot saved to screenshot.png")
        
        browser.close()

if __name__ == "__main__":
    take_screenshot()
