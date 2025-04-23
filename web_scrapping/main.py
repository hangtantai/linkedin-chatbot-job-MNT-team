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
from web_scrapping.commands.pagination_command import PaginationCommand


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

        # Wait for human verification if needed
        print("If a CAPTCHA or verification prompt appears, please solve it manually.")
        print("The script will wait for your input before continuing.")
        input("Press Enter after completing any verification steps (or if none appeared)...")

        # Job search URL
        search_url = config["search_link"]

        # Pagination page
        pagination = PaginationCommand(driver, search_url)
        pagination_urls = pagination.execute()
        
         # Prepare link file
        link_file = os.path.join(os.path.dirname(__file__), config["link_file"])
        
        # Ensure the file is empty to start (create or truncate)
        with open(link_file, 'w') as f:
            pass
        
        # Process each pagination URL to extract job links
        all_links = {} 
        for page_num, url in pagination_urls.items():
            try:
                logger.info(f"Processing page {page_num} with URL: {url}")
                
                # Navigate to the page
                driver.get(url)
                
                # Save the page HTML
                save_page = SavePageCommand(driver, url, link_file)
                save_page.execute()
                
                # Extract job links from this page
                link_extractor = ExtractorFactory.create_extractor("link")
                page_links = link_extractor.extract(link_file)
                if page_links:
                    logger.info(f"Extracted {len(page_links)} job links from page {page_num}")
                    all_links.update(page_links)
                else:
                    logger.warning(f"No job links found on page {page_num}")
                
            except Exception as e:
                logger.error(f"Failed to extract page {page_num} with URL {url}: {str(e)}")
                continue
        
        # Check if we found any job links
        if not all_links:
            logger.error("No job links found across all pages")
            return
            
        logger.info(f"Total job links extracted from all pages: {len(all_links)}")
        # Save all extracted links to the main link file (overwrite)
        with open(link_file, 'w') as f:
            for name, link in all_links.items():
                f.write(f"{link}\n")
        
        # Process job details from all collected links
        details_file = os.path.join(os.path.dirname(__file__), config["detail_file"])
        process_job = ProcessJobCommand(driver, all_links, details_file)
        data = process_job.execute()
        
        # destination directory
        final_directory = os.path.join(os.path.dirname(__file__), config["job_data"])
        
        # Use JobRepository for persistence operations
        job_repo = JobRepository(final_directory, s3_helper)

        # Save results and upload to S3 if successful
        if job_repo.save(data):
            job_repo.upload_to_s3(config["job_data"])
            logger.info(f"Successfully uploaded job data to S3 bucket: {config['s3_bucket']}")

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