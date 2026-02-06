from test import By  # noqa: F403
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


about_contaier_XPATH = '''//div[@id='about']/ancestor::section//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@class,"--is-collapsed")]'''

def get_my_about_section(driver):
    wait = WebDriverWait(driver, 10)

    try:
        about_div = wait.until(EC.presence_of_element_located((By.ID, "about")))
        # 2. Scroll to it to trigger rendering
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", about_div)
    except:  # noqa: E722
        print("❌ About section not found.")
        return []

    direct_span_xpath = '''//div[@id='about']/ancestor::section//span[contains(@class,"visually-hidden")][1]/ancestor::div[contains(@class,"--is-collapsed")]//span[contains(@class,"visually-hidden")]'''

    span = driver.find_element(By.XPATH, direct_span_xpath )

    about_text = span.get_attribute("innerText").strip() if span else ""

    # print("✅ About text extracted") if about_text else print("❌ No about text found")
    # print(about_text) if about_text else print("❌ No about text found")
    
    return about_text

# =================================================== :Code Execution: ===================================================

# url = "https://www.linkedin.com/in/nigar-saiyad-pmp%C2%AE-a37665273/"

# driver = get_driver()
# login_linkedin(driver=driver, username=username, password=password)
# driver.get(url)
# time.sleep(5)
# about_1 = get_my_about_section(driver)

# print("====" * 20)

# url = "https://www.linkedin.com/in/sakshi-raj0504/"
# driver.get(url)
# about_2 = get_my_about_section(driver)

# print("====" * 20)

# url = "https://www.linkedin.com/in/laxmimerit"
# driver.get(url)
# about_3 = get_my_about_section(driver)

# profile_data = {}

# profile_data['about_1'] = about_1
# profile_data['about_2'] = about_2
# profile_data['about_3'] = about_3

# # print(profile_data)
# print(json.dumps(profile_data, indent=2, ensure_ascii=False))