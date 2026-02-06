import os
import json
import time
import random 
from test import * # get_driver, login_linkedin, username, password
from name_headline import get_name, get_headline
from about import get_my_about_section
from educations import extract_education_info_dynamic
from experience import get_full_experience
from courses import extract_courses_info_dynamic
from projects import extract_projects_info_dynamic
from license_and_certifications import extract_licenses_and_certifications_info_dynamic


def full_scraper(driver, url):
    
    driver.get(url)
    time.sleep(random.randint(3, 5)) 

    name = get_name(driver)
    time.sleep(random.randint(1, 3))

    headline = get_headline(driver)
    time.sleep(random.randint(2, 4))

    about_text = get_my_about_section(driver)
    time.sleep(random.randint(3, 5))  

    education_data = extract_education_info_dynamic(driver)
    time.sleep(random.randint(2, 8)) 

    experience_data = get_full_experience(driver)
    time.sleep(random.randint(1, 6))

    projects_data = extract_projects_info_dynamic(driver)
    time.sleep(random.randint(5, 9))

    courses_data = extract_courses_info_dynamic(driver)
    time.sleep(random.randint(2, 4)) 

    l_and_c_data = extract_licenses_and_certifications_info_dynamic(driver)
    time.sleep(random.randint(3, 7)) 

    profile_data = {}

    profile_data['name'] = name
    profile_data['headline'] = headline
    profile_data['about'] = about_text
    profile_data['education'] = education_data
    profile_data['experience'] = experience_data
    profile_data['projects'] = projects_data
    profile_data['courses'] = courses_data
    profile_data['licenses_and_certifications'] = l_and_c_data
    
    return profile_data

def save_profile_data(profile_data, profile_url):
    # Extract LinkedIn username from URL
    profile_name = profile_url.rstrip('/').split('/')[-1]
    
    # Ensure the `data` directory exists
    os.makedirs("data", exist_ok=True)
    
    # Set filename
    filename = f"data/{profile_name}_linkedin_data.json"
    
    # Save JSON
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved data for {profile_name} at {filename}")

driver = get_driver()
login_linkedin(driver=driver, username=username, password=password)

# url = "https://www.linkedin.com/in/sakshi-raj0504/"
# url = "https://www.linkedin.com/in/manthan-mistry161200/"
# result = full_scraper(driver, url)
# save_profile_data(result, url)

# print("====" * 20)
# time.sleep(30)

url = "https://www.linkedin.com/in/laxmimerit"
result = full_scraper(driver, url)
save_profile_data(result, url)
