from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from web_scrapping.utils.logger import logger

class DriverManager:
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DriverManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DriverManager()
        return cls._instance
    
    def initialize_driver(self):
        """Setup and return Chrome Driver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_experimental_option("detach", True)
            # chrome_options.add_argument("--headless")

            self._driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome Driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome Driver: {str(e)}")
            raise
    
    def get_driver(self):
        if self._driver is None:
            self.initialize_driver()
        return self._driver
    
    def quit(self):
        if self._driver:
            self._driver.quit()
            self._driver = None
            logger.info("Browser session close")

# intialize singleton pattern
driver_manager = DriverManager.get_instance()