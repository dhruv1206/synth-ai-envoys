import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


options = webdriver.ChromeOptions()
options.headless = False
browser = webdriver.Chrome(options=options)

browser.get(f"https://pib.gov.in/allRel.aspx")
time.sleep(10)

ministries = WebDriverWait(browser, 10).until(
    ec.presence_of_all_elements_located((By.XPATH, """//select[@name="ctl00$ContentPlaceHolder1$ddlMinistry"]/option"""))
)
print(set(map(lambda x: x.text, ministries)))