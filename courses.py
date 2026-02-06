from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from test import *  # noqa: F403

Inline_courses_div_XPATH = '''//div[@id='courses']/ancestor::section//ul/li//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@data-view-name,"profile-component-entity")]'''
Extended_courses_div_XPATH = '''//section[contains(@class,"artdeco-card pb3")]//ul/li//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@data-view-name,"profile-component-entity")]'''

def extract_courses_info_dynamic(driver):
    wait = WebDriverWait(driver, 10)

    # 1. Scroll to education section
    try:
        courses_div = wait.until(EC.presence_of_element_located((By.ID, "courses")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", courses_div)
        time.sleep(1)
    except:  # noqa: E722
        print("❌ courses section not found.")
        return {"courses": []}
    
    used_show_all_button = False

    # 2. Handle "Show all education"
    try:
        show_all_button = wait.until(EC.presence_of_element_located((By.ID, "navigation-index-see-all-courses")))
        # print("✅ 'Show all courses' button found. Clicking it.")
        show_all_button.click()
        time.sleep(2)
        xpath_to_use = Extended_courses_div_XPATH
        used_show_all_button = True
    except:  # noqa: E722
        # print("ℹ️ Using inline courses path.")
        xpath_to_use = Inline_courses_div_XPATH

    # 3. Locate containers
    try:
        containers = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_to_use)))
        # print(f"✅ Found {len(containers)} courses containers.")
    except:  # noqa: E722
        print("❌ No courses containers found.")
        return {"courses": []}

    # 4. Extract data from containers

    courses_data = []

    for container in containers:
        try:
            spans = WebDriverWait(container, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, ".//span[contains(@class, 'visually-hidden')]"))
            )
            if not spans:
                print("❌ No spans found in container.")
                continue
            
            entry = {}

            for i, span in enumerate(spans):
                text = span.get_attribute("innerText").strip()
                if i == 0:
                    entry["name"] = text
                    continue
                elif len(text.split()) > 5:
                    entry["description"] = text
                
            courses_data.append(entry)

        except Exception as e:
            print(f"❌ Error extracting data from container: {e}")  

    # Go back to main profile if we had opened 'Show all'
    if used_show_all_button:
        driver.back()
        time.sleep(1)  

    return courses_data


# =================================================== :Testing:

# url = "https://www.linkedin.com/in/nigar-saiyad-pmp%C2%AE-a37665273/"
# driver = get_driver()
# login_linkedin(driver=driver, username=username, password=password)
# driver.get(url)
# time.sleep(5)
# result = extract_courses_info_dynamic(driver)
# print(json.dumps(result, indent=2, ensure_ascii=False))

# print("====" * 20)

# url = "https://www.linkedin.com/in/sakshi-raj0504/"
# driver.get(url)
# result_2 = extract_courses_info_dynamic(driver)
# print(json.dumps(result_2, indent=2, ensure_ascii=False))

# print("====" * 20)

# url = "https://www.linkedin.com/in/laxmimerit"
# driver.get(url)
# result_3 = extract_courses_info_dynamic(driver)
# print(json.dumps(result_3, indent=2, ensure_ascii=False))
