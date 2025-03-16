from selenium.webdriver.common.by import By
from web_scrapping.commands.base_command import Command
from web_scrapping.utils.logger import logger
from web_scrapping.utils.config import Config

class LoginCommand(Command):
    """Command to log in to LinkedIn"""
    
    def __init__(self, driver, email: str, password: str):
        """
        Initialize the command
        
        Args:
            driver: WebDriver instance
            email: Email/username for login
            password: Password for login
        """
        super().__init__()
        self.driver = driver
        self.email = email
        self.password = password
        self.logged_in = False
        self.add_metadata("target site", "Linkedin")
    
    def validate(self) -> bool:
        """Check if login can proceed"""
        if not self.email or not self.password:
            logger.error("Email or Password missing")
            return False
        return True
    
    def execute(self) -> bool:
        """Execute the login command"""
        try:
            config = Config.get_config()
            url = config["domain_login"]
            self.driver.get(url)
            
            # Get username field
            email_field = self.driver.find_element(By.ID, 'username')
            email_field.send_keys(self.email)
            
            # Get password field
            password_field = self.driver.find_element(By.ID, 'password')
            password_field.send_keys(self.password)
            
            # Submit username and password
            password_field.submit()
            logger.info("Successfully logged into LinkedIn")
            self.logged_in = True
            return True
        except Exception as e:
            logger.error(f"Failed to login to LinkedIn: {str(e)}")
            return False
    
    def undo(self) -> bool:
        """Logout from LinkedIn (if logged in)"""
        if not self.logged_in:
            return True
            
        try:
            config = Config.get_config()
            # This is a simplified example - actual logout may require different steps
            self.driver.get(config["domain_logout"])
            logger.info("Successfully logged out from LinkedIn")
            self.logged_in = False
            return True
        except Exception as e:
            logger.error(f"Failed to logout from LinkedIn: {str(e)}")
            return False