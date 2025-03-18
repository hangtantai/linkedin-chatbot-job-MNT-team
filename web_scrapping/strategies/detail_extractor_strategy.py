from bs4 import BeautifulSoup
import pandas as pd
from web_scrapping.strategies.extractor_strategy import ExtractorStrategy
from web_scrapping.utils.logger import logger

class DetailExtractorStrategy(ExtractorStrategy):
    """Strategy for extracting job details from a saved HTML page"""
    
    def extract(self, file_name: str, url: str) -> pd.DataFrame:
        """
        Extract job details from HTML page
        
        Args:
            source: Path to HTML file
            
        Returns:
            DataFrame containing job details
        """
        # initialize job data
        job_data = {}

        # read content from file
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                content = file.read()
                logger.info(f"Successfully read file: {file_name}")
        except (FileNotFoundError, IOError) as e:
            logger.error(f"Error reading file: {file_name}")
            print(f"File {file_name} not found.")
            return pd.DataFrame()

        try:
            # Direction:
            # h1 -> name
            # location -> div.job-details-jobs-unified-top-card__primary-description-container div first span
            # role: button.job-details-preferences-and-skills get all information from span.white-space-pre
            # details: article class: jobs-description__container jobs-description__container--condensed div lass mt4 get all content


            # convert text to Soup
            soup = BeautifulSoup(content, "html.parser")

            # main container
            main_container = soup.find("main")
            if not main_container:
                logger.warning("Main container not found in HTML")
                return pd.DataFrame()

            try:
                # get title of job
                job_title = main_container.find("h1").get_text().strip()
                if job_title:
                    job_data["job_title"] = job_title
                    logger.info(f"Successfully extracted job title info")
                else:
                    job_data["job_title"] = None
                    logger.warning(f"Job title not found")
            except AttributeError as e:
                logger.error(f"Failed to extract job title with problem: {str(e)}")
                job_data["job_title"] = None

            # get company name
            try:
                company_name_container = main_container.find("div", class_="job-details-jobs-unified-top-card__company-name")

                if company_name_container:
                    company_link = company_name_container.find("a")
                    company_name = company_link.get_text(strip=True) if company_link else None
                    job_data["company_name"] = company_name
                    logger.info(f"Successfully extracted company name info")
                else:
                    job_data["company_name"] = None
                    logger.warning(f"Company name not found")

            except Exception as e:
                logger.error(f"Failed to extract company name with problem: {str(e)}")
                job_data["company_name"] = None
            
            # url to linkedin 
            try:
                if url:
                    job_data["url"] = url
                    logger.info("Successfully extracted url info")
                else:
                    job_data["url"] = None
                    logger.warning(f"Url not found")
            except Exception as e:
                logger.error(f"Failed to extract url to linkedin job")
                job_data["url"] = None
            
            # get location, time, applicants
            try:
                location_time_appli_container = main_container.find("div", class_="job-details-jobs-unified-top-card__primary-description-container")

                # extract location, time, applicants
                if location_time_appli_container:
                    extracted = location_time_appli_container.get_text(separator=' ', strip=True)
                    splitted_element = extracted.split("·")
                    
                    # save it
                    job_data.update({
                        "job_location": splitted_element[0].strip(),
                        "job_time_posted": splitted_element[1].strip(),
                        "job_applicants_applied": splitted_element[2].strip()
                    })
                    logger.info(f"Successfully extracted location/time/applicants info")
                
                else:
                    logger.warning(f"Location/Time/Container container not found")
                    job_data.update({
                        "job_location": None,
                        "job_time_posted": None,
                        "job_applicants_applied": None
                    })

            except Exception as e:
                logger.error(f"Error extracting location/time/applicants: {str(e)}")
                job_data.update({
                    "job_location": None,
                    "job_time_posted": None,
                    "job_applicants_applied": None
                })

            # get role of job
            try:
                # create list to save
                role_list = []
                
                role_container = main_container.find("button", class_="job-details-preferences-and-skills")
                if role_container:
                    role_container_span = role_container.find_all("span")
                    # iter all elements in role container
                    for ele in role_container_span:
                        if ele:
                            # exclude visually-hidden class, because it is not necessary
                            if 'visually-hidden' not in ele.get('class', []):
                                role = ele.get_text(separator=' ', strip=True)
                                # avoiding duplicate data
                                if role and "Matches" not in role:
                                    role_list.append(role)

                    # join 2 elements
                    job_data["job_role"] = ",".join(role_list) if role_list else None
                    logger.info(f"Successful extracted job role")
                else:
                    job_data["job_role"] = None
                    logger.warning(f"Role container not found")
            except Exception as e:
                logger.error(f"Error extracting job role: {str(e)}")
                job_data["job_role"] = None

            try:
                # detail information of the job
                details_container = main_container.find("article", class_="jobs-description__container jobs-description__container--condensed")
                if details_container:
                    # main container of this process
                    details_cotainer_div = details_container.find("div", class_="mt4")
                    if details_cotainer_div:
                        job_data["job_details"]  = details_cotainer_div.get_text(separator='\n', strip=True)
                        logger.info(f"Successfully extracted detail information of the job")
                else:
                    logger.warning(f"Detail information not found")
                    job_data["job_details"] = None
            except Exception as e:
                logger.error(f"Error extracting detail information of the job with the problem: {str(e)}")
                job_data["job_details"] = None

            # convert dictionary to data frame
            job_df = pd.DataFrame([job_data])
            logger.info("Successfully created DataFrame with job information")
            return job_df

        except Exception as e:
            logger.error(f"Critical error in extraction detail information from html with problem: {str(e)}")
            return pd.DataFrame()
        