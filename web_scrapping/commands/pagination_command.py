from web_scrapping.commands.base_command import Command
from web_scrapping.driver.driver_manager import driver_manager 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from web_scrapping.utils.config import Config
from web_scrapping.utils.logger import logger

config = Config.get_config()
class PaginationCommand(Command):
    """Command to navigate linkedin page"""
    def __init__(self, driver, url: str, page_number: int = None):
        """
        Initlize the command

        Args:
            driver: WebDriver instance
        """
        super().__init__()
        self.driver = driver
        self.origin_url = url
        self.page_number = page_number
        self.pagination_container = None
        self.add_metadata("extracted page", page_number)

    def _get_pagination_container(self):
        """Get the pagination container element"""
        if self.pagination_container is None:
            self.pagination_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config["ul_class"]))
            )
        return self.pagination_container

    def get_total_page(self) -> int:
        """Count and Return the total number of pages in the pagination bar"""
        container = self._get_pagination_container()
        page_buttons = container.find_elements(By.XPATH, config["li_class"])
        total_pages = len(page_buttons)
        return total_pages

    def get_current_page(self) -> int:
        """Get the current active page number"""
        container = self._get_pagination_container()
        current_page_element = container.find_element(By.XPATH, config["li_active"])
        return int(current_page_element.get_attribute(config["btn_class"]))
    
    def navigate_to_page(self, target_page: str) -> dict[str, str]:
        """Navigate to a specific page number"""
        try:
            urls = {}
            container = self._get_pagination_container()
            
            # Use XPATH with correct syntax
            page_button = container.find_element(
                By.XPATH, f".//li[@{config['btn_class']}='{target_page}']/button"
            )
            page_button.click()
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logger.info(f"Successfully navigated to page {target_page}")
            url = self.driver.current_url
            urls[target_page] = url
            return urls
        except Exception as e:
            logger.error(f"Error navigating to page {target_page}: {str(e)}")
            return False
    
    def navigate_to_next_page(self) -> dict[str, str]:
        """Navigate to the next page"""
        try:
            container = self._get_pagination_container()
            current_page = self.get_current_page()
            total_pages = self.get_total_page()
            
            # Check if we're already on the last page
            if current_page >= total_pages:
                logger.info(f"Already on the last page ({current_page})")
                return False
            
            # Find and click the next page button
            next_page = current_page + 1
            next_page_button = container.find_element(
                By.XPATH, f".//li[@{config['btn_class']}='{next_page}']/button"
            )
            next_page_button.click()
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            current_url = self.driver.current_url
            logger.info(f"Successfully navigated to page {next_page}")

            return current_url
        except Exception as e:
            logger.error(f"Error navigating to next page: {str(e)}")
            return False


    def execute(self) -> bool:
        """Navigate and extract data from pages"""
        try:
            self.driver.get(self.origin_url)
            total_pages = self.get_total_page()
            logger.info(f"Found {total_pages} pages total")
            
            if self.page_number is not None:
                # Extract from a specific page
                if self.page_number < 1 or self.page_number > total_pages:
                    if total_pages == 1:
                        output_text = "1 page"
                    else:
                        output_text = f"1 - {total_pages} pages"
                    logger.error(f"Page number {self.page_number} is out of range {output_text}")
                    return False
                
                else:
                    url = self.navigate_to_page(self.page_number)
                    return url
            else:
                # Extract from all pages, starting with current page
                current_page = self.get_current_page()
                logger.info(f"Starting extraction from page {current_page} of {total_pages}")
                
                # Create a dictionary to store URLs
                page_urls = {}
                
                # Get URL of current page
                current_url = self.driver.current_url
                page_urls[current_page] = current_url
                
                # Extract from current page first
                if hasattr(self, 'extract_function') and self.extract_function:
                    logger.info(f"Extracting data from page {current_page}: {current_url}")
                    self.extract_function(self.driver)
                
                # Continue with remaining pages
                next_url = self.navigate_to_next_page()
                while next_url:
                    current_page = self.get_current_page()
                    page_urls[current_page] = next_url
                    next_url = self.navigate_to_next_page()
                
                logger.info("Completed extraction from all pages")
                # Return all collected URLs
                self.add_metadata("page_urls", page_urls)
                return page_urls
                
        except Exception as e:
            logger.error(f"Error in pagination execution: {str(e)}")
            return False
        
    def undo(self) -> bool:
        pass