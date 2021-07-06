"""
    docstring value
"""
import os
from playwright.sync_api import sync_playwright
from testframework.libraries.logger import logger

class TestWeb:
    """
        some value
    """

    def __init__(self):
        pass

    def run_test(self):
        """

        :return:
        """
        try:
            with sync_playwright() as playwright_object:
                chrome_path = os.path.join(os.getcwd(),
                                           'testframework\\tools\\chrome-win\\chrome.exe')
                browser = playwright_object.chromium.launch(headless=False, executable_path=chrome_path)
                page = browser.new_page()
                page.goto("http://playwright.dev")
                logger.Info(page.title())
                browser.close()
        except Exception as e:
            print(e)
