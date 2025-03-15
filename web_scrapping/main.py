# Import necessary library
import os
import warnings
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from typing import Dict
import streamlit as st

# Import necessary functions
from web_scrapping.extract_link import extract_link
from web_scrapping.extract_detail import extract_detail_information
from web_scrapping.logger import logger
from web_scrapping.s3_helpers import s3_helper

def setup_chrome_driver() -> webdriver.Chrome:
    """Setup and return Chrome Driver with appropriate options"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_experimental_option("detach", True)
        # chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome Driver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome Driver: {str(e)}")
        raise

def linkedin_login(driver: webdriver.Chrome, email_address: str, password_text: str) -> None:
    """Login to Linkedin using provided credentials"""
    try:
        url = 'https://linkedin.com/login'
        driver.get(url)

        # login process
        # get username field
        email_field = driver.find_element(By.ID, 'username')
        email_field.send_keys(email_address)

        # get password field
        password_field = driver.find_element(By.ID, 'password')
        password_field.send_keys(password_text)

        # submit username and password
        password_field.submit()
        logger.info("Successfully logged into Linkedin")
    except Exception as e:
        logger.error(f"Failed to login to Linkedin: {str(e)}")
        raise

def save_page_content(driver: webdriver.Chrome, url: str, output_file: str) -> None:
    """Save webpage content to a file"""
    try:
        driver.get(url)
        
        # parse the content with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Write the text to a file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(soup.prettify())
        logger.info(f"Successfully saved page content to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save page content: {str(e)}")
        raise

def process_job_links(driver: webdriver.Chrome, link_data: Dict[str, str], output_file: str) -> pd.DataFrame:
    """Process each job link and extract detailed information"""
    data = pd.DataFrame()
    processed_count = 0
    
    try:
        total_links = len(link_data)
        logger.info(f"Starting to process {total_links} job links")
        
        for job_title, link_path in link_data.items():
            try:
                url = f"https://www.linkedin.com{link_path}"
                save_page_content(driver, url, output_file)
                
                job_df = extract_detail_information(output_file)  # Using imported function directly
                if not job_df.empty:
                    data = pd.concat([data, job_df], ignore_index=True)
                    processed_count += 1
                    logger.info(f"Processed job {processed_count}/{total_links}: {job_title}")
                else:
                    logger.warning(f"No data extracted for job: {job_title}")
                    
            except Exception as e:
                logger.error(f"Failed to process job {job_title}: {str(e)}")
                continue
                
        logger.info(f"Successfully processed {processed_count} out of {total_links} jobs")
        return data
    except Exception as e:
        logger.error(f"Critical error in job processing: {str(e)}")
        return data

def main():
    try:
        # Suppress warnings
        warnings.filterwarnings("ignore")
        
        # Get credentials
        email_address = st.secrets["EMAIL"]
        password_text = st.secrets["PASSWORD"]
        
        # Initialize WebDriver and login
        driver = setup_chrome_driver()
        linkedin_login(driver, email_address, password_text)
        
        # Job search URL
        search_url = "https://www.linkedin.com/jobs/search/?currentJobId=4105549838&distance=25&f_E=1&f_PP=102267004&geoId=104195383&keywords=data%20engineer&origin=JOB_SEARCH_PAGE_KEYWORD_HISTORY&refresh=true"
        
        # Extract job links
        link_file = os.path.join(os.path.dirname(__file__), 'output.txt')
        save_page_content(driver, search_url, link_file)
        link_extracted = extract_link(link_file)  # Using imported function directly
        
        if not link_extracted:
            logger.error("No job links found")
            return
            
        # Process job details
        details_file = os.path.join(os.path.dirname(__file__), 'details.txt')
        data = process_job_links(driver, link_extracted, details_file)
        
        # destination directory
        final_directory = os.path.join(os.path.dirname(__file__), 'job_data.csv')
        
        # Save results
        if not data.empty:
            data.to_csv(final_directory, index=False)
            logger.info("Successfully saved job data to CSV")

            # Upload to s3
            if s3_helper.upload_file(final_directory, "job_data.csv"):
                logger.info("Successfully uploaded job data to S3")
            else:
                logger.error("Failed to upload job data to S3")

        else:
            logger.warning("No job data to save")
            
    except Exception as e:
        logger.error(f"Critical error in main process: {str(e)}")
    
    finally:
        try:
            driver.quit()
            logger.info("Browser session closed")

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
            logger.error(f"Failed to close browser: {str(e)}")

if __name__ == "__main__":
    main()