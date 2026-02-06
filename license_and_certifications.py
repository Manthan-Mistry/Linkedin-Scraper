from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from test import *  # noqa: F403

Inline_l_andc_div_XPATH = '''//div[@id="projects"]/ancestor::section//ul/li//div[contains(@data-view-name,"profile-component-entity")]'''
Extendes_l_and_c_div_XPATH = '''//section[contains(@class,"artdeco-card pb3")]//ul/li//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@data-view-name,"profile-component-entity")]'''


section_id = "navigation-index-see-all-licenses-and-certifications"

def extract_licenses_and_certifications_info_dynamic(driver):
    wait = WebDriverWait(driver, 10)

    # 1. Scroll to education section
    try:
        l_and_c_div = wait.until(EC.presence_of_element_located((By.ID, "licenses_and_certifications")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", l_and_c_div)
        time.sleep(1)
    except:  # noqa: E722
        print("❌ licenses_and_certifications section not found.")
        return []

    used_show_all_button = False

    # 2. Handle "Show all education"
    try:
        show_all_button = wait.until(EC.presence_of_element_located((By.ID, "navigation-index-see-all-licenses-and-certifications")))
        # print("✅ 'Show all projects' button found. Clicking it.")
        show_all_button.click()
        time.sleep(2)
        xpath_to_use = Extendes_l_and_c_div_XPATH
        used_show_all_button = True
    except:  # noqa: E722
        print("ℹ️ Using inline licenses_and_certifications path.")
        xpath_to_use = Inline_l_andc_div_XPATH

    # 3. Locate containers
    try:
        containers = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_to_use)))
        # print(f"✅ Found {len(containers)} projects containers.")
    except:  # noqa: E722
        print("❌ No licenses_and_certifications containers found.")
        return []
    
    # Duration regex
    issued_regex = re.compile(
        r'\bIssued\b\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\.?\s?\d{4}',
        re.IGNORECASE
    )

    
    licenses_and_certifications_data = []

    for container in containers:
        try:
            spans = container.find_elements(By.XPATH, ".//span[contains(@class, 'visually-hidden')]")
            if not spans:
                print("❌ No spans found.")
                continue

            entry = {}
            seen_keys = set()

            for i, span in enumerate(spans):
                text = span.get_attribute("innerText").strip()

                if i == 0:
                    entry["name"] = text
                    continue

                if i == 1:
                    entry["Institution"] = text

                if "skills:" in text.lower():
                    entry["skills"] = text.replace("Skills:", "").strip()
                    seen_keys.add("skills")

                elif issued_regex.search(text):
                    entry["issue_date"] = text
                    seen_keys.add("issue_date")

                elif "." in text and len(text.split()) > 10:
                    entry["description"] = text
                    seen_keys.add("description")

            licenses_and_certifications_data.append(entry)

        except Exception as e:
            print(f"❌ Error processing container: {e}")
            continue

    # Go back to main profile if we had opened 'Show all'
    if used_show_all_button:
        driver.back()
        time.sleep(1)  

    return licenses_and_certifications_data


# url = "https://www.linkedin.com/in/laxmimerit"

# driver = get_driver()
# login_linkedin(driver=driver, username=username, password=password)
# driver.get(url)
# time.sleep(5)
# result_1 = extract_licenses_and_certifications_info_dynamic(driver)
# print(json.dumps(result_1, indent=2, ensure_ascii=False))


# print("====" * 20)
# time.sleep(5)
# url = "https://www.linkedin.com/in/sakshi-raj0504/"
# driver.get(url)
# result_2 = extract_licenses_and_certifications_info_dynamic(driver)
# print(json.dumps(result_2, indent=2, ensure_ascii=False))


# print("====" * 20)
# time.sleep(5)
# url = "https://www.linkedin.com/in/nigar-saiyad-pmp%C2%AE-a37665273/"
# driver.get(url)
# result_3 = extract_licenses_and_certifications_info_dynamic(driver)
# print(json.dumps(result_3, indent=2, ensure_ascii=False))


