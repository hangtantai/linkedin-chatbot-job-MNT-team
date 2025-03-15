import pandas as pd
from typing import Dict
from web_scrapping.commands.base_command import Command
from web_scrapping.commands.page_command import SavePageCommand
from web_scrapping.utils.logger import logger
from web_scrapping.factories.extractor_factory import ExtractorFactory
from web_scrapping.utils.config import Config

class ProcessJobCommand(Command):
    """Command to process job links and extract details"""

    def __init__(self, driver, link_data: Dict[str, str], output_file: str):
        """
        Initialize the command
        
        Args:
            driver: WebDriver instance
            link_data: Dictionary mapping job titles to their LinkedIn paths
            output_file: Path where the job details will be temporarily saved
        """
        self.driver = driver
        self.link_data = link_data
        self.output_file = output_file
        self.data = pd.DataFrame()
        self.processed_count = 0
        # Create the detail extractor strategy
        self.detail_extractor = ExtractorFactory.create_extractor("detail")
        
    def execute(self):
        """Execute the process job links command"""
        try:
            config = Config.get_config()
            total_links = len(self.link_data)
            logger.info(f"Starting to process {total_links} job links")
            
            for job_title, link_path in self.link_data.items():
                try:
                    # Construct full URL
                    url = f"{config['domain']}{link_path}"
                    
                    # Use SavePageCommand to get the job details page
                    save_command = SavePageCommand(self.driver, url, self.output_file)
                    save_command.execute()
                    
                    # Extract information from the saved page
                    job_df = self.detail_extractor.extract(self.output_file)
                    
                    if not job_df.empty:
                        self.data = pd.concat([self.data, job_df], ignore_index=True)
                        self.processed_count += 1
                        logger.info(f"Processed job {self.processed_count}/{total_links}: {job_title}")
                    else:
                        logger.warning(f"No data extracted for job: {job_title}")
                        
                except Exception as e:
                    logger.error(f"Failed to process job {job_title}: {str(e)}")
                    continue
                    
            logger.info(f"Successfully processed {self.processed_count} out of {total_links} jobs")
            return self.data
        except Exception as e:
            logger.error(f"Critical error in job processing: {str(e)}")
            return self.data
    
    def undo(self):
        """Undo the processing operation (not applicable)"""
        # Job processing cannot be undone in a meaningful way
        logger.warning("Undo operation not supported for ProcessJobCommand")
        return False
        
    def get_results(self):
        """Get the results of processing"""
        return self.data