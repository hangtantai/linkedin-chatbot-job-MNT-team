# Import necessary library
import os
import warnings
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
warnings.filterwarnings("ignore")

# Import necessary function
import web_scrapping.extract_link as extract_link
import web_scrapping.extract_detail as extract_detail

# Call environment
load_dotenv()

# Get username and password to Linkedin
email = os.environ["EMAIL"]
password = os.environ["PASSWORD"]

# driver
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_experimental_option("detach", True)
# chrome_options.add_argument("--headless")

# driver
driver = webdriver.Chrome(options=chrome_options)
url = 'https://linkedin.com/login'
driver.get(url)

# get username
email = driver.find_element(By.ID, 'username')
email.send_keys(os.environ['EMAIL'])

# get password
password = driver.find_element(By.ID, 'password')
password.send_keys(os.environ['PASSWORD'])

# submit username and password
password.submit()

# declare url
url = "https://www.linkedin.com/jobs/search/?currentJobId=4105549838&distance=25&f_E=1&f_PP=102267004&geoId=104195383&keywords=data%20engineer&origin=JOB_SEARCH_PAGE_KEYWORD_HISTORY&refresh=true"
driver.get(url)

# parse the content with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Write the text to a file
file_name_extracted_link_input = 'output.txt'
with open(file_name_extracted_link_input, 'w', encoding='utf-8') as file:
    file.write(soup.prettify())

# process extract link
link_extracted = extract_link.extract_link(file_name_extracted_link_input)

# Process each link to get all information about job
data = pd.DataFrame()
for i in link_extracted:
    url = "https://www.linkedin.com" + link_extracted[i]
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract all text from the soup object
    text = soup.get_text()

    # Write the text to a file
    file_name_detailed = 'details.txt'
    with open(file_name_detailed, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    # process extract detail
    job_df = extract_detail.extract_detail_information(file_name_detailed)
    data = pd.concat([data, job_df], ignore_index=True)

print("Successfully, all done")
data.to_csv("job_data.csv", index=False)