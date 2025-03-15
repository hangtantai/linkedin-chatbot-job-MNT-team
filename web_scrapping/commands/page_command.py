from bs4 import BeautifulSoup
from web_scrapping.commands.base_command import Command
from web_scrapping.utils.logger import logger
import os

class SavePageCommand(Command):
    """Command to save a web page's content to a file"""
    
    def __init__(self, driver, url, output_file):
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
        self.output_file = output_file
        self.saved = False
        # Keep track of original content if any for undo
        self.original_content = None
        self.add_metadata("target url", url)
        self.add_metadata("output path", output_file)
    
    def validate(self):
        """Check if save operation can proceed"""
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except:
                logger.error(f"Cannot create output directory {output_dir}")
                return False
        return True
    
    def execute(self):
        """Execute the save page command"""
        try:
            # Check if file exists and store original content
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r', encoding='utf-8') as file:
                    self.original_content = file.read()
            
            self.driver.get(self.url)
            
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Write the text to a file
            with open(self.output_file, 'w', encoding='utf-8') as file:
                file.write(soup.prettify())
                
            logger.info(f"Successfully saved page content to {self.output_file}")
            self.saved = True
            return True
        except Exception as e:
            logger.error(f"Failed to save page content: {str(e)}")
            return False
    
    def undo(self):
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