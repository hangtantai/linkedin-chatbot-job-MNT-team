# from web_scrapping.s3_helpers import S3Helper
# import streamlit as st
# import os

# bucket_name = st.secrets["S3_BUCKET_JOB"]
# s3_helper = S3Helper(bucket_name)

# # Test upload
# # link_file = os.path.join(os.path.dirname(__file__), 'output.txt')
# # s3_helper.upload_file(link_file, "test.txt")

# # Test read
# content = s3_helper.read_file("job_data.csv")
# print(content)

# from web_scrapping.utils.config import Config

# config = Config.get_config()
# email = config["email"]
# print(email)



from web_scrapping.driver.driver_manager import driver_manager 
from web_scrapping.commands.login_command import LoginCommand
from web_scrapping.utils.config import Config
from web_scrapping.commands.pagination_command import PaginationCommand
import os
config = Config.get_config()

# Get credentials
email_address = config["email"]
password_text = config["password"]
driver = driver_manager.get_driver()
page_number = 2
login = LoginCommand(driver, email_address, password_text)
login.execute()

search_url = config["search_link"]
# link_file = os.path.join(os.path.dirname(__file__), config["link_file"])
# save_page = SavePageCommand(driver, search_url, link_file)
# save_page.execute()



# pagination = PaginationCommand(driver,search_url)
# pagination_url = pagination.execute()
# print(pagination_url)
# # Wait for pagination container to be visible
# pagination_container = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.CSS_SELECTOR, "ul.artdeco-pagination__pages"))
# )

# # Count all page buttons
# page_buttons = pagination_container.find_elements(By.XPATH, ".//li[@data-test-pagination-page-btn]")
# total_pages = len(page_buttons)
# print(f"Total pages in navigation bar: {total_pages}")


# if page_number is not None:
#     # Find and click specific page number
#     page_button = pagination_container.find_element(
#         By.XPATH, f".//li[@data-test-pagination-page-btn='{page_number}']/button"
#     )
#     page_button.click()
# else:
#     # Find the current active page
#     current_page_element = pagination_container.find_element(
#         By.XPATH, ".//li[contains(@class, 'active')]"
#     )
#     current_page = int(current_page_element.get_attribute("data-test-pagination-page-btn"))
    
#     # Find and click the next page button
#     next_page = current_page + 1
#     next_page_button = pagination_container.find_element(
#         By.XPATH, f".//li[@data-test-pagination-page-btn='{next_page}']/button"
#     )
#     next_page_button.click()

# # Wait for page to load
# WebDriverWait(driver, 10).until(
#     lambda d: d.execute_script("return document.readyState") == "complete"
# )

# current_page_url = driver.current_url
# print(current_page_url)
