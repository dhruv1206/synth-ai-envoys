import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from Models.OriginalPressRelease import OriginalPressRelease


def scrape_pib():
    options = webdriver.ChromeOptions()
    options.headless = False
    browser = webdriver.Chrome(options=options)

    content_area_class = "content-area"
    ministry_heading_class = "font104"
    ul_class = "num"
    detail_page_main_content_class = "innner-page-main-about-us-content-right-part"
    detail_page_title_class = "text-center"
    detail_page_image_class_selector = "img:not([alt]), img[alt='']"
    detail_page_twitter_image_class = "css-9pa8cd"
    detail_page_paragraph_xpath = "//p[contains(@style, 'text-align:justify')][not(normalize-space()='&nbsp;')]"
    detail_page_twitter_post_class_name = "blockquote[class='twitter-tweet']"
    date_select_name = "ctl00$ContentPlaceHolder1$ddlday"
    month_select_name = "ctl00$ContentPlaceHolder1$ddlMonth"
    year_select_name = "ctl00$ContentPlaceHolder1$ddlYear"
    browser.get(f"https://pib.gov.in/allRel.aspx")
    time.sleep(5)
    selected_date = browser.find_element(By.NAME, date_select_name).find_element(By.CSS_SELECTOR, "option[selected]")
    selected_month = browser.find_element(By.NAME, month_select_name).find_element(By.CSS_SELECTOR, "option[selected]")
    selected_year = browser.find_element(By.NAME, year_select_name).find_element(By.CSS_SELECTOR, "option[selected]")
    todays_date_in_milliseconds = datetime.strptime(f"{selected_date.text} {selected_month.text} {selected_year.text}",
                                                    "%d %B %Y").timestamp() * 1000

    try:
        content_area = WebDriverWait(browser, 10).until(
            ec.presence_of_all_elements_located((By.CLASS_NAME, content_area_class)))

        ministry_headings = list(
            map(lambda x: x.text, content_area[0].find_elements(By.CLASS_NAME, ministry_heading_class)))

        ul_items = content_area[0].find_elements(By.CLASS_NAME, ul_class)
        pr_links = {}

        for i, ul in enumerate(ul_items):
            pr_links[ministry_headings[i]] = list(map(lambda x: x.find_element(By.TAG_NAME, "a").get_attribute("href"),
                                                      ul.find_elements(By.TAG_NAME, "li")))

        original_press_releases_dict = {}

        for key, value in pr_links.items():
            original_press_releases = []
            for link in value:
                pr_id = link.split("PRID=")[1]
                browser.get(link)

                main_content = WebDriverWait(browser, 10).until(
                    ec.presence_of_element_located((By.CLASS_NAME, detail_page_main_content_class))
                )

                title = main_content.find_elements(By.CLASS_NAME, detail_page_title_class)[1].find_element(By.TAG_NAME,
                                                                                                           "h2").text

                paragraphs = main_content.find_elements(By.XPATH, detail_page_paragraph_xpath)
                paragraphs = list(map(lambda x: x.text, paragraphs))
                content = "\\".join(paragraphs)

                image_urls = list(map(lambda x: x.get_attribute("src"),
                                      main_content.find_elements(By.CSS_SELECTOR, detail_page_image_class_selector)))
                # twitter_posts = []
                # time.sleep(5)
                # try:
                #     twitter_posts = WebDriverWait(browser, 5).until(
                #         ec.presence_of_all_elements_located((By.CLASS_NAME, detail_page_twitter_image_class)))
                # except Exception as e:
                #     pass
                # image_urls += list(map(lambda x: x.get_attribute("src"), filter(lambda x: x.get_attribute("alt") == "Image", twitter_posts)))
                # print(image_urls)
                original_press_releases.append(OriginalPressRelease(pr_id, title, content, image_urls))
            original_press_releases_dict[key] = original_press_releases

        return original_press_releases_dict, todays_date_in_milliseconds

    except Exception as e:
        browser.quit()
        return {}


if __name__ == "__main__":
    data = scrape_pib()
    print(data)
