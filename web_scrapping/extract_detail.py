# import library if not import
from bs4 import BeautifulSoup
import pandas as pd
def extract_detail_information(file_name: str) -> pd.DataFrame:
    """
    Extracts detailed job information from HTML content and updates the provided DataFrame

    Args:
        content (str): the HTML content as string
        data (pd.DataFrame): The DataFrame to update with extracted job information (empty)

    Returns:
        pd.DataFrame: the update DataFrame with extracted information
    """
    # read content from file
    with open(file_name, "r", encoding="utf-8") as file:
        content = file.read()

    # convert text to Soup
    soup = BeautifulSoup(content, "html.parser")
    job_data = {}

    # Direction:
    # h1 -> name
    # location -> div.job-details-jobs-unified-top-card__primary-description-container div first span
    # role: button.job-details-preferences-and-skills get all information from span.white-space-pre
    # details: article class: jobs-description__container jobs-description__container--condensed div lass mt4 get all content

    # main container
    main_container = soup.find("main")

    # get title of job
    job_title = main_container.find("h1").get_text().strip()
    job_data["job_title"] = job_title

    # get location, time, applicants
    location_time_appli_container = main_container.find("div", class_="job-details-jobs-unified-top-card__primary-description-container")

    # extract location, time, applicants
    if location_time_appli_container:
        extracted = location_time_appli_container.get_text(separator=' ', strip=True)
        splitted_element = extracted.split("·")
        job_location = splitted_element[0]
        job_time_posted = splitted_element[1]
        job_applicants_applied = splitted_element[2]
    else:
        print("Job Location, Time and Applicants not found.")
    # save into database
    job_data["job_location"] = job_location
    job_data["job_time_posted"] = job_time_posted
    job_data["job_applicants_applied"] = job_applicants_applied

    # get role of job
    role_container = main_container.find("button", class_="job-details-preferences-and-skills")
    role_container_span = role_container.find_all("span")

    # create list to save
    role_list = []

    # iter all elements in role container
    for ele in role_container_span:
        if ele:
            # exclude visually-hidden class, because it is not necessary
            if 'visually-hidden' not in ele.get('class', []):
                role = ele.get_text(separator=' ', strip=True)
                # avoiding duplicate data
                if "Matches" not in role:
                    role_list.append(role)
        else:
            print("Job location container not found.")

    # delete empty data
    role_list = [role for role in role_list if role]

    # join 2 elements
    job_role = ",".join(role_list)
    job_data["job_role"] = job_role

    # detail information of the job
    details_container = main_container.find("article", class_="jobs-description__container jobs-description__container--condensed")

    # main container of this process
    details_cotainer_div = details_container.find("div", class_="mt4")
    if details_cotainer_div:
        job_details = details_cotainer_div.get_text(separator='\n', strip=True)
        job_data["job_details"] = job_details

    # convert dictionary to data frame
    job_df = pd.DataFrame([job_data])
    print("Successfully: extracted information")
    return job_df