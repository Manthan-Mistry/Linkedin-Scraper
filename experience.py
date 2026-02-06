from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from test import *  # noqa: F403

Experience_container_div_xpath = '''//div[@id='experience']/ancestor::section//ul/li//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@data-view-name,"profile-component-entity")]'''
# Experience_container_div_xpath = '''//section[@id="experience"]//ul/li[.//div[contains(@data-view-name,"profile-position-entity")]]'''


# Regex to detect LinkedIn duration-like text
DURATION_REGEX = re.compile(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*-\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4})')

# =================================== :Simple (Non-Nested) Experience Parsing: ==================================

def parse_simple_experience_block(block):
    try:
        # Only take first 3 visible texts (e.g., Role, Company, Duration)
        spans = block.find_elements(By.XPATH, './/span[contains(@class, "visually-hidden")]')
        texts = [s.text.strip() for s in spans if s.text.strip()][:3]

        # print(f"🔍 Extracted texts: {texts}")
        if len(texts) < 2:
            return None

        # Step 1: Identify role — from t-bold block
        role_span = block.find_elements(By.XPATH, './/div[contains(@class,"t-bold")]//span[contains(@class,"visually-hidden")]')
        role = role_span[0].text.strip() if role_span else texts[0]

        # Step 2: Identify duration using regex
        duration = ""
        duration_regex = re.compile(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[-–]\s*(?:Present|\w+\s+\d{4})')
        for t in texts:
            if "mos" in t or "yrs" in t or duration_regex.search(t):
                duration = t
                break

        # Step 3: Remaining text is likely the company
        known_vals = {role, duration, "Full-time", "Internship", "Hybrid", "Remote"}
        company = next((t for t in texts if t not in known_vals), "")

        return {
            "company_name": company,
            "designations": [
                {
                    "role": role,
                    "duration": duration
                }
            ]
        }

    except Exception as e:
        print(f"❌ Error parsing simple experience block: {e}")
        return None

def get_simple_experience(driver):
    wait = WebDriverWait(driver, 10)

    try:
        experience_sec = wait.until(EC.presence_of_element_located((By.ID, "experience")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", experience_sec)
        time.sleep(1)
    except:  # noqa: E722
        print("❌ Experience section not found.")
        return {"experience": []}

    experience_data = []

    try:
        blocks_xpath = '''//div[@id='experience']/ancestor::section//ul/li//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@data-view-name,"profile-component-entity")]/ancestor::li[contains(@class, "artdeco-list__item")]/div'''
        experience_blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, blocks_xpath)))
        # print(f"✅ Found {len(experience_blocks)} top-level experience blocks.")

        for i, block in enumerate(experience_blocks):
            spans = block.find_elements(By.XPATH, './/span[contains(@class, "visually-hidden")]')
            if len(spans) <= 7:  # Considered simple
                parsed = parse_simple_experience_block(block)
                if parsed:
                    experience_data.append(parsed)
            else:
                print(f"🔁 Skipping nested experience block at index {i} (has {len(spans)} spans).")

    except Exception as e:
        print(f"❌ Error locating experience blocks: {e}")
        return {"experience": []}

    return {"experience": experience_data}

# =================================== :Final Nested Experience Parsing: =========================================

def parse_nested_role_block(role_block):
    try:
        # Extract company name from parent container
        company_name_xpath = '''.//ancestor::li//div[contains(@class,"t-bold")]//span[contains(@class,"visually-hidden")]'''
        company_name_span = role_block.find_element(By.XPATH, company_name_xpath)
        company = company_name_span.text.strip() if company_name_span else ""

        # Extract total duration from parent container (outside each role)
        try:
            total_duration_xpath = '''.//ancestor::li//a//span[contains(@class,"t-14")]'''
            total_duration_span = role_block.find_element(By.XPATH, total_duration_xpath)
            total_duration = total_duration_span.text.strip().split("\n")[0] if total_duration_span else ""
        except:  # noqa: E722
            total_duration = ""

        # Get span texts inside the role block
        spans = role_block.find_elements(By.XPATH, './/span[contains(@class, "visually-hidden")]')
        texts = [s.text.strip() for s in spans if s.text.strip()]

        role, duration = "", ""

        # Get role from bold span or fallback to first text
        role_span = role_block.find_elements(By.XPATH, './/div[contains(@class,"t-bold")]//span[contains(@class,"visually-hidden")]')
        role = role_span[0].text.strip() if role_span else (texts[0] if texts else "")

        # Match full or abbreviated months in duration
        duration_regex = re.compile(
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\s+\d{4}\s*[-–]\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\s+\d{4})',
            re.IGNORECASE
        )

        for t in texts:
            if "mos" in t or "yrs" in t or "yr" in t or duration_regex.search(t):
                duration = t
                break

        return {
            "company_name": company,
            "total_duration": total_duration,
            "role": role,
            "duration": duration
        }

    except Exception as e:
        print(f"❌ Error parsing nested role: {e}")
        return None

def get_nested_experience(driver):
    wait = WebDriverWait(driver, 10)

    try:
        experience_sec = wait.until(EC.presence_of_element_located((By.ID, "experience")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", experience_sec)
        time.sleep(1)
    except:  # noqa: E722
        print("❌ Experience section not found.")
        return {"experience": []}

    grouped_experience = defaultdict(lambda: {"designations": [], "duration": ""})

    try:
        blocks_xpath = '''//div[@id='experience']/ancestor::section//ul/li//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@data-view-name,"profile-component-entity")]/ancestor::li[not(contains(@class, "artdeco-list__item"))]/div'''
        role_blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, blocks_xpath)))
        # print(f"✅ Found {len(role_blocks)} nested role blocks.")

        for block in role_blocks:
            parsed = parse_nested_role_block(block)
            if parsed:
                company = parsed["company_name"]
                grouped_experience[company]["designations"].append({
                    "designation": parsed["role"],
                    "duration": parsed["duration"]
                })

                if not grouped_experience[company]["duration"]:
                    grouped_experience[company]["duration"] = parsed["total_duration"]

        # Format final list
        final_output = []
        for company, info in grouped_experience.items():
            final_output.append({
                "company_name": company,
                "duration": info["duration"],
                "designations": info["designations"]
            })

        return {"experience": final_output}

    except Exception as e:
        print(f"❌ Error parsing nested roles: {e}")
        return {"experience": []}

# ===============================================================================================================


def get_full_experience(driver):
    wait = WebDriverWait(driver, 10)

    try:
        experience_sec = wait.until(EC.presence_of_element_located((By.ID, "experience")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", experience_sec)
        time.sleep(1)
    except:  # noqa: E722
        print("❌ Experience section not found.")
        return {"experience": []}

    final_experience = defaultdict(lambda: {"designations": [], "duration": ""})

    # Get simple blocks
    try:
        simple_xpath = '''//div[@id='experience']/ancestor::section//ul/li//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@data-view-name,"profile-component-entity")]/ancestor::li[contains(@class, "artdeco-list__item")]/div'''
        simple_blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, simple_xpath)))
        for block in simple_blocks:
            spans = block.find_elements(By.XPATH, './/span[contains(@class, "visually-hidden")]')
            if len(spans) <= 7:
                parsed = parse_simple_experience_block(block)
                if parsed:
                    final_experience[parsed["company_name"]]["designations"].extend(parsed["designations"])
    except Exception as e:
        print(f"❌ Simple block error: {e}")

    # Get nested blocks
    try:
        nested_xpath = '''//div[@id='experience']/ancestor::section//ul/li//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@data-view-name,"profile-component-entity")]/ancestor::li[not(contains(@class, "artdeco-list__item"))]/div'''
        nested_blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, nested_xpath)))
        for block in nested_blocks:
            parsed = parse_nested_role_block(block)
            if parsed:
                final_experience[parsed["company_name"]]["designations"].append({
                    "designation": parsed["role"],
                    "duration": parsed["duration"]
                })
                if not final_experience[parsed["company_name"]]["duration"]:
                    final_experience[parsed["company_name"]]["duration"] = parsed["total_duration"]
    except Exception as e:
        print(f"❌ Nested block error: {e}")

    return [
        {
            "company_name": k,
            "duration": v["duration"],
            "designations": v["designations"]
        } for k, v in final_experience.items()
    ]

# ===============================================================================================================


# driver = get_driver()
# login_linkedin(driver=driver, username=username, password=password)

# url = "https://www.linkedin.com/in/sakshi-raj0504/"
# driver.get(url)
# time.sleep(5)
# experience_data = get_full_experience(driver)

# print(json.dumps(experience_data, indent=2, ensure_ascii=False))


# print("=====" * 50)


# url = "https://www.linkedin.com/in/laxmimerit"
# driver.get(url)
# experience_data_1 = get_full_experience(driver)

# print(json.dumps(experience_data_1, indent=2, ensure_ascii=False))

# print("=====" * 50)

# url = "https://www.linkedin.com/in/nigar-saiyad-pmp%C2%AE-a37665273/"
# driver.get(url)
# experience_data_2 = get_full_experience(driver)

# print(json.dumps(experience_data_2, indent=2, ensure_ascii=False))















































































































# wait = WebDriverWait(driver, 10)

# # 1. Scroll to education section
# try:
#     experience_div = wait.until(EC.presence_of_element_located((By.ID, "experience")))
#     driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", experience_div)
#     time.sleep(1)
#     print("Experience section found and scrolled into view.")
# except:
#     print("❌ Education section not found.")
#     # return {"education": []}

# # Step 1: Find all top-level experience blocks
# exp_blocks = driver.find_elements(By.XPATH, '//div[@id="experience"]/following-sibling::div//ul/li[not(ancestor::li)]')

# print(len(exp_blocks), "experience blocks found.")

# # Step 2: Loop through each experience block and extract info
# for i in range(len(exp_blocks)):
#     xpath = f'(//div[@id="experience"]/following-sibling::div//ul/li[not(ancestor::li)])[{i+1}]//div[contains(@data-view-name,"profile-component-entity")]//span[contains(@class,"visually-hidden")]'
#     spans = driver.find_elements(By.XPATH, xpath)
#     texts = [s.text.strip() for s in spans if s.text.strip()]

#     print("=" * 20)
#     for text in texts:
#         print(text)



# ================================================= :Data: ================================================

# ✅ Experience section found and scrolled into view.
# # 2 experience blocks found.
# ====================
# ====================
# [{'company_name': 'Rapido', 'duration': '9 mos', 'designations': [{'designation': 'Bengaluru, Karnataka, India', 'duration': '', 'location': ''}, {'designation': 'Data Analyst Intern', 'duration': 'Oct 2024 to Present · 9 mos', 'location': ''}]}, {'company_name': 'Unified Mentor · Internship', 'duration': 'Aug 2024 to Sep 2024 · 2 mos', 'designations': [{'designation': 'Remote', 'duration': '', 'location': ''}]}]
# ✅ Experience section found and scrolled into view.
# # 4 experience blocks found.
# ====================
# ====================
# ====================
# ====================
# [{'company_name': 'Linedata · Full-time', 'duration': 'Sep 2024 to Present · 10 mos', 'designations': [{'designation': 'Mumbai, Maharashtra, India', 'duration': '', 'location': ''}]}, {'company_name': 'Full-time · 4 yrs 10 mos', 'duration': 'Assistant Vice President', 'designations': [{'designation': 'Oct 2023 to Sep 2024 · 1 yr', 'duration': '', 'location': ''}, 
# {'designation': 'Mumbai, Maharashtra, India · On-site', 'duration': 'Dec 2019 to Apr 2021 · 1 yr 5 mos', 'location': 'Bengaluru, Karnataka, India'}]}, {'company_name': 'mBreath', 'duration': '3 yrs 4 mos', 'designations': [{'designation': 'Co-Founder', 'duration': '', 'location': ''}, {'designation': 'Data Scientist', 'duration': '', 'location': ''}]}, {'company_name': 'Indian Institute of Technology, Kharagpur', 'duration': '4 yrs 8 mos', 'designations': [{'designation': 'Student', 'duration': '', 'location': ''}, {'designation': 'Jan 2013 to Jan 2017 · 4 yrs 1 mo', 'duration': '', 'location': ''}, {'designation': 'IIT Kharagpur', 'duration': '', 'location': ''}]}]


# ====================================:Prompt:===================================

# ok lets simplify things and consider below scenarios;
# there will be two kinds of experience 1. simple, 2. nested
# in simple experience heres the structure of the spans;
# 1. 1st span is post name (i.e. Data Analyst, Senior Manager etc)
# 2. 2nd span has company name (i.e.  Linedata, Unified Mentor) remove . Fulltime from this 
# 3. 3rd span will have duration (i.e. Fulltime, May 2025 - Present · 2 mos) remove . x mos from this

# now this below is nersted experience (i.e. one with same company but different posts)
# 1. 1st span (whole experience div not nest parts div) will be company name always
# 2. 2nd span (whole experience div not nest parts div) will have TOTAL duration in that company not seperate post duration (i.e. 9mos, Full-time  . 4yrs 10mos) remove Full-time . from this
# from 2rd span we will have structure like this below for nested roles;
# 1. 1st span inside nested div will be post (i.e. Assistance Vice President, Data Analyst Intern etc)
# 2. 2nd div can have either duration or employement type (i.e. Oct 2023 - Sep 2024, Fulltime) remove Fulltime or Internship in the 2nd span if found
# 3. 3rd span will have duration if the 2nd span had Fulltime/Internship in case of dutaion in 2nd span i dont want 3rd span
# here are some example for nested experience;

# IGP
# Full-time · 4 yrs 10 mos
# Assistant Vice President
# Oct 2023 - Sep 2024 · 1 yr
# Mumbai, Maharashtra, India
# 👉Customer Behavior Modeling:
# Estimating Customer Lifetime Value (CLV) predicts customer worth, churn forecasts retention, and purchase propensity gauges transaction counts and spending. Tier transition analysis influences segmentation, retention, and personalized marketing, enhancing satisfaction, loyalty, and revenue.

# 👉Hashtag Search:
# Enhancing search functionality by integrating product attributes into phrases for a more intuitive and efficient product discovery process.

# 👉Automated Customer Feedback Report:
# Utilizing fine-tuning of a Large Language Model to generate diverse supervised data, addressing imbalances in actual data for improved analysis and data-driven decision-making in customer satisfaction and issue resolution.

# 👉Meta Tag Generator for PLP, PDP, and Query Pages:
# The "Meta Tag Generator" project automates meta tag creation for PLP, PDP, and Query Pages, optimizing search engine visibility and attracting targeted traffic to the website.👉Customer Behavior Modeling: Estimating Customer Lifetime Value (CLV) predicts customer worth, churn forecasts retention, and purchase propensity gauges transaction counts and spending. Tier transition analysis influences segmentation, retention, and personalized marketing, enhancing satisfaction, loyalty, and revenue. 👉Hashtag Search: Enhancing search functionality by integrating product attributes into phrases for a more intuitive and efficient product discovery process. 👉Automated Customer Feedback Report: Utilizing fine-tuning of a Large Language Model to generate diverse supervised data, addressing imbalances in actual data for improved analysis and data-driven decision-making in customer satisfaction and issue resolution. 👉Meta Tag Generator for PLP, PDP, and Query Pages: The "Meta Tag Generator" project automates meta tag creation for PLP, PDP, and Query Pages, optimizing search engine visibility and attracting targeted traffic to the website.…see more

# Associate Vice President
# Apr 2021 - Oct 2023 · 2 yrs 7 mos
# Mumbai, Maharashtra, India · On-site
# 👉Personalized Search:
# Engineered dynamic product ranking tailored to individual users, optimizing the search experience based on user preferences.

# 👉Graph and Big Data Analysis:
# Designed and implemented graph and big-data analysis tools to extract valuable insights, contributing to strategic decision-making.

# 👉Implicit Customer Features Identification:
# Utilized demographic data, including religion, native region, and gender, to drive targeted marketing, resulting in personalized recommendations and search suggestions aligned with individual preferences.

# 👉Social Graph Analytics for Personalized Search and Recommendation:
# Analyzed user social graphs and click journeys to develop sophisticated recommendation systems, providing personalized suggestions based on user behavior and connections.

# 👉Customer Segmentation and Ranking:
# Implemented techniques to segment customers based on diverse attributes and ranked them according to relevance and potential value, enhancing the personalization of product rankings.

# 👉Image Segmentation and Phrase Generation:
# Applied image segmentation techniques to enrich e-commerce product attributes and utilized phrase generation to create descriptive and informative content.

# 👉Customer Purchase Intention and Cart Value Prediction:
# Developed models for predicting customer purchase intentions and cart values, contributing to optimized marketing strategies and an improved shopping experience.

# 👉User Category and MRP Affinity:
# Explored user categories and their affinity towards specific products or price ranges, leveraging insights to enhance personalized recommendations and targeted marketing efforts.

# 👉Social Graph-Based Occasion Marking and Relation Prediction:
# Leveraged the social graph to identify occasions and predict user relationships, facilitating personalized recommendations aligned with specific events or social connections.👉Personalized Search: Engineered dynamic product ranking tailored to individual users, optimizing the search experience based on user preferences. 👉Graph and Big Data Analysis: Designed and implemented graph and big-data analysis tools to extract valuable insights, contributing to strategic decision-making. 👉Implicit Customer Features Identification: Utilized demographic data, including religion, native region, and gender, to drive targeted marketing, resulting in personalized recommendations and search suggestions aligned with individual preferences. 👉Social Graph Analytics for Personalized Search and Recommendation: Analyzed user social graphs and click journeys to develop sophisticated recommendation systems, providing personalized suggestions based on user behavior and connections. 👉Customer Segmentation and Ranking: Implemented techniques to segment customers based on diverse attributes and ranked them according to relevance and potential value, enhancing the personalization of product rankings. 👉Image Segmentation and Phrase Generation: Applied image segmentation techniques to enrich e-commerce product attributes and utilized phrase generation to create descriptive and informative content. 👉Customer Purchase Intention and Cart Value Prediction: Developed models for predicting customer purchase intentions and cart values, contributing to optimized marketing strategies and an improved shopping experience. 👉User Category and MRP Affinity: Explored user categories and their affinity towards specific products or price ranges, leveraging insights to enhance personalized recommendations and targeted marketing efforts. 👉Social Graph-Based Occasion Marking and Relation Prediction: Leveraged the social graph to identify occasions and predict user relationships, facilitating personalized recommendations aligned with specific events or social connections.…see more

# Data Science Manager
# Dec 2019 - Apr 2021 · 1 yr 5 mos
# Bengaluru, Karnataka, India

# ====================================



# Rapido
# 9 mos
# Bengaluru, Karnataka, India

# Data Analyst
# Full-time
# May 2025 - Present · 2 mos

# Data Analyst Intern
# Internship
# Oct 2024 - Present · 9 mos
# Hybrid