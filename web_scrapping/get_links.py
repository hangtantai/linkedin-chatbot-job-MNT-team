from web_scrapping.driver.driver_manager import driver_manager 
from web_scrapping.utils.config import Config
from web_scrapping.commands.login_command import LoginCommand
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

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
human_verification_done = input("Press Enter after completing any verification steps (or if none appeared)...")


search_field = driver.find_element(By.CSS_SELECTOR, "div#global-nav-typeahead.search-global-typeahead__typeahead input")
search_field.send_keys("Data Engineer Intern")
search_field.send_keys(Keys.RETURN)



options_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div#search-reusables__filters-bar.search-reusables__filters-bar-grouping ul.search-reusables__filter-list"))
    )
first_li_button = options_field.find_element(By.CSS_SELECTOR, "li:first-child button")
first_li_button.click()


location_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input[id^='jobs-search-box-location-id-ember']"))
)
location_field.send_keys(Keys.CONTROL + "a")  # Select all text
location_field.send_keys(Keys.DELETE)         # Delete selected text
location_field.send_keys("Ho Chi Minh City, Vietnam")
location_field.send_keys(Keys.RETURN)

# Get the current URL of the jobs search page
current_url = driver.current_url
print(f"Current jobs search URL: {current_url}")

# Optionally, you can save this URL to a file or variable for later use
link_file = os.path.join(os.path.dirname(__file__), config["search_file"])
with open(link_file, "w") as f:
    f.write(current_url)

driver.quit()