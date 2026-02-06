from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

from test import *  # noqa: F403

Inline_educations_div_XPATH = '''//div[@id='education']/ancestor::section//ul/li//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@data-view-name,"profile-component-entity")]'''
Extendes_education_div_XPATH = '''//section[contains(@class,"artdeco-card pb3")]//ul/li//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@data-view-name,"profile-component-entity")]'''


# ✅ Working correctly except dynamic dict key assignment:
# def extract_education_info(driver):
#     wait = WebDriverWait(driver, 10)

#     # 1. Scroll to education section to trigger lazy-loading
#     try:
#         education_div = wait.until(EC.presence_of_element_located((By.ID, "education"))) 
#         driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", education_div)
#         time.sleep(1)  # Let the section load if lazy-rendered
#     except:
#         print("❌ Education section not found.")
#         return {"education": []}

#     # 2. Check and click "Show all x educations" if available
#     try:
#         show_all_button = wait.until(
#             EC.element_to_be_clickable((By.XPATH, "//button//span[contains(text(), 'Show all') and contains(text(), 'educations')]"))
#         )
#         show_all_button.click()
#         time.sleep(2)
#         xpath_to_use = Extendes_education_div_XPATH
#         print("education container found in extended section")
#     except:
#         # Use inline education path if button is not present
#         xpath_to_use = Inline_educations_div_XPATH
#         print("education container found in inline section")

#     # 3. Get all education containers using WebDriverWait
#     try:
#         containers = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_to_use)))
#     except:
#         print("❌ No education containers found.")
#         return {"education": []}

#     education_data = []

#     for container in containers:
#         try:
#             spans = WebDriverWait(container, 5).until(
#                 EC.presence_of_all_elements_located((By.XPATH, ".//span[contains(@class, 'visually-hidden')]"))
#             )
#             # span_texts = [span.text.strip() for span in spans if span.text.strip()]
#             if not spans:
#                 print("❌ No spans found in container.")
#                 continue

#             entry = {
#                 "school": spans[0].get_attribute("innerText") if len(spans) > 0 else "",
#                 "degree": spans[1].get_attribute("innerText") if len(spans) > 1 else "",
#                 "duration": spans[-1].get_attribute("innerText") if len(spans) > 2 else ""
#             }
#             education_data.append(entry)
#         except:
#             continue

#     print(education_data)

#     return {"education": education_data}



# ✅ Working correctly except dynamic dict key assignment:
def extract_education_info_dynamic(driver):
    wait = WebDriverWait(driver, 10)

    # 1. Scroll to education section
    try:
        education_div = wait.until(EC.presence_of_element_located((By.ID, "education")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", education_div)
        time.sleep(1)
    except:  # noqa: E722
        print("❌ Education section not found.")
        return {"education": []}

    used_show_all_button = False

    # 2. Handle "Show all education"
    try:
        show_all_button = wait.until(EC.presence_of_element_located((By.ID, "navigation-index-see-all-education")))
        # print("✅ 'Show all education' button found. Clicking it.")
        show_all_button.click()
        time.sleep(2)
        xpath_to_use = Extendes_education_div_XPATH
        used_show_all_button = True
    except:  # noqa: E722
        print("ℹ️ Using inline education path.")
        xpath_to_use = Inline_educations_div_XPATH

    # 3. Locate containers
    try:
        containers = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_to_use)))
        # print(f"✅ Found {len(containers)} education containers.")
    except:  # noqa: E722
        print("❌ No education containers found.")
        return {"education": []}

    # Duration regex
    duration_regex = re.compile(
        r'(?:'
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+\d{4}'  # Jan 2020
        r'\s*-\s*'
        r'(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\.?\s*\d{4})'  # May 2023 or Present
        r'|'
        r'\d{4}\s*-\s*(?:Present|\d{4})'  # 2018 - 2021 or 2018 - Present
        r')',
        re.IGNORECASE
    )

    education_data = []

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

                if "institution" not in entry:
                    entry["institution"] = text
                    continue

                if "skills:" in text.lower():
                    entry["skills"] = text.replace("Skills:", "").strip()
                    seen_keys.add("skills")

                elif "yrs" in text or "yr" in text or "mos" in text or duration_regex.search(text):
                    entry["duration"] = text
                    seen_keys.add("duration")

                elif "." in text and len(text.split()) > 15:
                    entry["description"] = text
                    seen_keys.add("description")

                elif "degree" not in seen_keys:
                    entry["degree"] = text
                    seen_keys.add("degree")

            education_data.append(entry)

        except Exception as e:
            print(f"❌ Error processing container: {e}")
            continue

    # Go back to main profile if we had opened 'Show all'
    if used_show_all_button:
        driver.back()
        time.sleep(1)

    return education_data


# =================================================== :Testing:

# url = "https://www.linkedin.com/in/nigar-saiyad-pmp%C2%AE-a37665273/"

# driver = get_driver()
# login_linkedin(driver=driver, username=username, password=password)
# driver.get(url)
# time.sleep(5)
# education_1 = extract_education_info_dynamic(driver)

# print("====" * 20)

# url = "https://www.linkedin.com/in/sakshi-raj0504/"
# driver.get(url)
# education_2 = extract_education_info_dynamic(driver)

# print("====" * 20)

# url = "https://www.linkedin.com/in/laxmimerit"
# driver.get(url)
# education_3 = extract_education_info_dynamic(driver)

# profile_data = {}

# profile_data['education_1'] = education_1
# profile_data['education_2'] = education_2
# # profile_data['education_3'] = education_3

# # print(profile_data)
# print(json.dumps(profile_data, indent=2, ensure_ascii=False))