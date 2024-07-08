import re
import json
from playwright.sync_api import sync_playwright, expect
import time
import os
from board_data import get_board_data  # Import the get_board_data function

COOKIES_PATH = 'cookies.json'

def save_cookies(context):
    cookies = context.cookies()
    with open(COOKIES_PATH, 'w') as f:
        json.dump(cookies, f)

def load_cookies(context):
    if os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, 'r') as f:
            cookies = json.load(f)
            context.add_cookies(cookies)

def run_playwright_script(api_key, board_id):
    def item_created(page):
        page.get_by_text("When this happens").click()
        page.get_by_test_id("search_combobox-search").fill("item created")
        page.get_by_test_id("combobox-option_0").get_by_text("item created").click()

    def create_subitem(page, name: str):
        page.get_by_test_id("search_combobox-search").fill("create subitem")
        page.get_by_test_id("combobox-option_0").get_by_text("create subitem").click()
        page.get_by_test_id("create a subitem").get_by_text("subitem").last.click()
        page.get_by_test_id("dialog").get_by_text("New item").click()
        textbox = page.get_by_test_id("dialog").get_by_role("textbox")
        textbox.press("ControlOrMeta+a")
        textbox.fill(name)
        textbox.press("Enter")
        status_cell = page.locator(".cell-wrapper > .cell-component > .status-cell-component > .status-cell-inner > .ds-text-component")
        status_cell.click()
        done_option = page.get_by_role("option", name="Done").locator("span")
        done_option.click()
        # Click the last child icon
        page.locator(".add-additional-action-button").last.click()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()

        # Load cookies if they exist
        load_cookies(context)
        
        page = context.new_page()
        
        # Navigate to the Monday.com board page
        page.goto(f"https://elevate-demo.monday.com/boards/{board_id}")
        
        # Wait for 15 seconds
        time.sleep(15)
        
        # Ensure the 'Add Automation to Board' button is visible
        add_automation_button = page.get_by_test_id("recipe-builder-add-automation-to-board-button").get_by_test_id("button")
        expect(add_automation_button).to_be_visible()

        # Get board data
        board_data = get_board_data()

        item_created(page)
        items = board_data.get('data', {}).get('boards', [])[0].get('items_page', {}).get('items', [])
        
        # Create subitems based on board data
        for item in items:
            subitem_names = [subitem['name'] for subitem in item.get('subitems', [])]
            for name in subitem_names:
                create_subitem(page, name)

        # Save cookies to file
        save_cookies(context)

        # Clean up
        context.close()
        browser.close()
