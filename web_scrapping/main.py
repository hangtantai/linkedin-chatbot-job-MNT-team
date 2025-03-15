# Import necessary library
import os
import warnings
from web_scrapping.factories.extractor_factory import ExtractorFactory
from web_scrapping.utils.logger import logger
from web_scrapping.helpers.s3_helpers import s3_helper
from web_scrapping.driver.driver_manager import driver_manager 
from web_scrapping.commands.login_command import LoginCommand
from web_scrapping.commands.page_command import SavePageCommand
from web_scrapping.commands.process_job_command import ProcessJobCommand
from web_scrapping.utils.config import Config
from web_scrapping.repository.job_repository import JobRepository
def main():
    try:
        # Suppress warnings
        warnings.filterwarnings("ignore")
        driver = driver_manager.get_driver()
        config = Config.get_config()
        
        # Get credentials
        email_address = config["email"]
        password_text = config["password"]
        
        # Login using the singleton driver
        login = LoginCommand(driver, email_address, password_text)
        login.execute()
        
        # Job search URL
        search_url = config["search_link"]
        
        # Extract job links
        link_file = os.path.join(os.path.dirname(__file__), config["link_file"])
        save_page = SavePageCommand(driver, search_url, link_file)
        save_page.execute()
        link_extractor = ExtractorFactory.create_extractor("link")
        link_extracted = link_extractor.extract(link_file)
        
        if not link_extracted:
            logger.error("No job links found")
            return
            
        # Process job details
        details_file = os.path.join(os.path.dirname(__file__), config["detail_file"])
        process_job = ProcessJobCommand(driver, link_extracted, details_file)
        data = process_job.execute()
        
        # destination directory
        final_directory = os.path.join(os.path.dirname(__file__), config["job_data"])
        
        # Use JobRepository for persistence operations
        job_repo = JobRepository(final_directory, s3_helper)

        # Save results and upload to S3 if successful
        if job_repo.save(data):
            job_repo.upload_to_s3(config["job_data"])

    except Exception as e:
        logger.error(f"Critical error in main process: {str(e)}")
    
    finally:
        try:
            # Use the driver_manager to quit
            driver_manager.quit()

            # Clean up temporary files
            if os.path.exists(link_file):
                os.remove(link_file)
                logger.info("Cleaned up output.txt")
            if os.path.exists(details_file):
                os.remove(details_file)
                logger.info("Cleaned up details.txt")
            if os.path.exists(final_directory):
                os.remove(final_directory)
                logger.info("Cleaned up job_data.csv")
        except Exception as e:
            logger.error(f"Failed to clean up resources: {str(e)}")

if __name__ == "__main__":
    main()