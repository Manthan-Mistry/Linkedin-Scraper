from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test import *  # noqa: F403

Headline_span_XPATH = '''//div[contains(@class,"text-body-medium break-words")]'''

def get_name(driver):
    name = driver.title.split(" | ")[0].split(")")[1].strip()
    return name

def get_headline(driver):
    wait = WebDriverWait(driver, 10)
    headline = wait.until(EC.presence_of_element_located((By.XPATH, Headline_span_XPATH))).get_attribute("innerText").strip()

    return headline


# url = "https://www.linkedin.com/in/nigar-saiyad-pmp%C2%AE-a37665273/"
# driver = get_driver()
# login_linkedin(driver=driver, username=username, password=password)
# driver.get(url)
# time.sleep(5)
# name = get_name(driver)
# headline = get_headline(driver)

# print(name)
# print(headline)

# print("=="*20)

# url = "https://www.linkedin.com/in/sakshi-raj0504/"
# driver.get(url)
# name = get_name(driver)
# headline = get_headline(driver)

# print(name)
# print(headline)

# print("=="*20)

# url = "https://www.linkedin.com/in/laxmimerit"
# driver.get(url)
# name = get_name(driver)
# headline = get_headline(driver)

# print(name)
# print(headline)