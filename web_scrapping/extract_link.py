# import library if not import
from bs4 import BeautifulSoup
from web_scrapping.logger import Logger

logger = Logger()
def extract_link(file_name: str, data: dict = None) -> dict:
    """
    Extracts link to detailed job

    Args:
        content (str): the HTML content as string
        data (dict): the dictionary to update link of job

    Returns:
        dict: the update dictionary with extracted information
    """
    # check if dataFrame is None
    if data is None:
        data = {}
    
    try:
        # read content from file
        with open(file_name, "r", encoding="utf-8") as file:
            content = file.read()
            logger.info(f"Successfully read file: {file_name}")
    except (FileNotFoundError, IOError) as e:
        logger.error(f"Error reading file: {file_name}")


    try:
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Main container
        main_container = soup.find('div', class_="scaffold-layout__list")
        if not main_container:
            logger.warning(f"Main container not found in HTML")
            return []
        
        try: 
            # Find all div tags within the main container
            div_tags = main_container.find_all('div')
            logger.info(f"Found {len(div_tags)} div tags in main container")

            list_elements = {}
            a_tags = []

            # Iterate through each div tag to find ul tags and their li children
            for index, div in enumerate(div_tags, 1):
                try:
                    ul_tag = div.find('ul')
                    if ul_tag:
                        li_tags = ul_tag.find_all('li')
                        logger.debug(f"Processing div {index}: Found {len(li_tags)} li tags")
                        
                        for li in li_tags:
                            try:
                                div = li.select_one("div > div > div.job-card-list__entity-lockup.artdeco-entity-lockup.artdeco-entity-lockup--size-4.ember-view > div > div > a")
                                if div is not None:
                                    a_tags.append(div)
                            except Exception as li_error:
                                logger.warning(f"Failed to process li tag: {str(li_error)}")
                                continue
                except Exception as div_error:
                    logger.warning(f"Failed to process div {index}: {str(div_error)}")
                    continue

            logger.info(f"Successfully collected {len(a_tags)} job links")

            # extract link
            successful_extracts = 0
            for a in a_tags:
                try:
                    key = a.get("aria-label")
                    value = a.get("href")
                    if key and value:
                        list_elements[key] = value
                        successful_extracts += 1
                    else:
                        logger.warning(f"Skipping link - Missing {'aria-label' if not key else 'href'}")
                except Exception as link_error:
                    logger.warning(f"Failed to extract link data: {str(link_error)}")
                    continue
                    
            logger.info(f"Successfully extracted {successful_extracts} links out of {len(a_tags)} found")
            return list_elements
        
        
        except Exception as e:
            logger.error(f"Error in link extraction process: {str(e)}", 
                        extra={
                            "div_tags_found": len(div_tags) if 'div_tags' in locals() else 0,
                            "a_tags_found": len(a_tags) if 'a_tags' in locals() else 0,
                            "successful_extracts": successful_extracts if 'successful_extracts' in locals() else 0
                        })
    
    
    except Exception as e:
        logger.error(f"Error in link extraction process: {str(e)}", 
                        extra={
                            "div_tags_found": len(div_tags) if 'div_tags' in locals() else 0,
                            "a_tags_found": len(a_tags) if 'a_tags' in locals() else 0,
                            "successful_extracts": successful_extracts if 'successful_extracts' in locals() else 0
                        })
        return []