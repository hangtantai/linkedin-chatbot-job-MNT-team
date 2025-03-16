from bs4 import BeautifulSoup
from web_scrapping.commands.base_command import Command
from web_scrapping.utils.logger import logger
import os
import time
import random
from selenium.webdriver.support.ui import WebDriverWait

class SavePageCommand(Command):
    """Command to save a web page's content to a file"""
    
    def __init__(self, driver, url: str, output_file: str, use_human: bool = True):
        """
        Initialize the command
        
        Args:
            driver: WebDriver instance
            url: URL of the page to save
            output_file: Path where the page content will be saved
        """
        super().__init__()
        self.driver = driver
        self.url = url
        self.use_human = use_human
        self.output_file = output_file
        self.saved = False
        # Keep track of original content if any for undo
        self.original_content = None
        self.add_metadata("target url", url)
        self.add_metadata("output path", output_file)
    
    def validate(self) -> bool:
        """Check if save operation can proceed"""
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except:
                logger.error(f"Cannot create output directory {output_dir}")
                return False
        return True
    
    def execute(self) -> bool:
        """Execute the save page command with anti-detection measures"""
        try:
            # Check if file exists and store original content
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r', encoding='utf-8') as file:
                    self.original_content = file.read()
            
            # Navigate to the URL
            self.driver.get(self.url)
            
            if self.use_human_simulation:
                # Wait for page to load with a random delay (1.5-3 seconds)
                time.sleep(random.uniform(1.5, 3))
                
                # Execute human-like browsing behavior
                self._simulate_human_browsing()
                
                # Try different extraction methods until we get valid content
                content = self._extract_content_with_retry()
            else:
                # Direct extraction without human simulation for better performance
                # Wait for page to load (standard wait)
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                # Extract page content directly
                content = self.driver.page_source
            
            if not content:
                logger.error("Failed to extract valid content")
                return False
            
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Write the text to a file
            with open(self.output_file, 'w', encoding='utf-8') as file:
                file.write(soup.prettify())
                
            logger.info(f"Successfully saved page content to {self.output_file}")
            self.saved = True
            return True
        except Exception as e:
            logger.error(f"Failed to save page content: {str(e)}")
            return False
    
    def _simulate_human_browsing(self) -> bool:
        """Simulate human-like browsing behavior to avoid detection"""
        try:
            # Random scroll down with smooth behavior
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Scroll down in multiple small increments
            num_steps = random.randint(5, 8)
            for i in range(1, num_steps + 1):
                # Calculate scroll position with some randomness
                target_position = min(i * scroll_height / num_steps, scroll_height - viewport_height)
                target_position = target_position * random.uniform(0.9, 1.1)
                
                # Execute scroll with smooth behavior
                self.driver.execute_script(f"window.scrollTo({{top: {target_position}, behavior: 'smooth'}})")
                
                # Wait a random amount of time between scrolls
                time.sleep(random.uniform(0.8, 2.0))
            
            # Sometimes scroll back up a bit
            if random.random() < 0.7:
                up_position = random.uniform(0.3, 0.7) * scroll_height
                self.driver.execute_script(f"window.scrollTo({{top: {up_position}, behavior: 'smooth'}})")
                time.sleep(random.uniform(0.5, 1.5))
            
            # Final scroll to ensure we see everything
            self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'})")
            time.sleep(random.uniform(1, 2))
            
            logger.debug("Human browsing simulation completed")
            return True
        except Exception as e:
            logger.warning(f"Error during human browsing simulation: {str(e)}")
            return False
    
    def _extract_content_with_retry(self, max_attempts: int = 3) -> str:
        """Extract page content using multiple methods with retries"""
        extraction_methods = [
            self._extract_with_page_source,
            self._extract_with_js_dom,
            self._extract_with_js_innerHTML
        ]
        
        for attempt in range(max_attempts):
            # Use a different method each time
            method = extraction_methods[attempt % len(extraction_methods)]
            method_name = method.__name__.replace("_extract_with_", "")
            
            try:
                logger.debug(f"Attempting extraction with method: {method_name}")
                content = method()
                
                # Verify the content seems valid
                if self._is_valid_content(content):
                    logger.debug(f"Extraction successful with {method_name}")
                    return content
                else:
                    logger.debug(f"Extraction with {method_name} produced invalid content")
            except Exception as e:
                logger.warning(f"Extraction attempt {attempt+1} with {method_name} failed: {str(e)}")
            
            # Slight delay between attempts
            time.sleep(random.uniform(1, 2))
        
        # If all methods fail, fall back to page_source as last resort
        logger.warning("All extraction methods failed, using page_source as fallback")
        return self.driver.page_source
    
    def _extract_with_page_source(self) -> str:
        """Extract content using standard page_source"""
        return self.driver.page_source
    
    def _extract_with_js_dom(self) -> str:
        """Extract content using JavaScript DOM serialization"""
        return self.driver.execute_script("""
            return (new XMLSerializer()).serializeToString(document);
        """)
    
    def _extract_with_js_innerHTML(self) -> str:
        """Extract content using document.documentElement.innerHTML"""
        return self.driver.execute_script("""
            return document.documentElement.outerHTML;
        """)
    
    def _is_valid_content(self, content: str) -> str:
        """Check if the extracted content appears to be valid"""
        if not content or len(content) < 1000:
            return False
            
        # Check for common LinkedIn job list elements
        job_markers = [
            'job-card-container',
            'job-result-card',
            'jobs-search-results',
            'artdeco-pagination'
        ]
        
        # Check for clear signs of anti-scraping measures
        blocking_markers = [
            'captcha',
            'unusual traffic',
            'please verify',
            'automated access',
            'security verification'
        ]
        
        # Count how many job markers we found
        found_markers = sum(1 for marker in job_markers if marker in content)
        found_blockers = sum(1 for blocker in blocking_markers if blocker.lower() in content.lower())
        
        # Valid if we have job markers and no blockers
        return found_markers >= 1 and found_blockers == 0
    
    def undo(self) -> None:
        """Undo the save operation by restoring original content"""
        if not self.saved:
            return True
            
        try:
            if self.original_content is not None:
                with open(self.output_file, 'w', encoding='utf-8') as file:
                    file.write(self.original_content)
                logger.info(f"Restored original content to {self.output_file}")
            else:
                if os.path.exists(self.output_file):
                    os.remove(self.output_file)
                    logger.info(f"Removed file {self.output_file}")
            
            self.saved = False
            return True
        except Exception as e:
            logger.error(f"Failed to undo save operation: {str(e)}")
            return False