import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from utils import download_image_from_url, upload_multiple_images_to_firebase, generate_random_string


def scrape_images(image_keywords):
    options = webdriver.ChromeOptions()
    options.headless = False
    browser = webdriver.Chrome(options=options)
    image_urls = []
    for i,query in enumerate(image_keywords):
        try:
            correct_query = query.replace(" ", "+")

            individual_image_selector_class = ".mNsIhb .YQ4gaf"

            browser.get(f"https://www.google.com/search?q={correct_query}&tbm=isch")

            images = WebDriverWait(browser, 10).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, individual_image_selector_class)))
            images = [image.get_attribute("src") for image in images]
            # print("Found {} images".format(images[0]))
            # image_urls.append(images[0])
            image_urls.append(download_image_from_url(images[0], f"{generate_random_string(10)}.jpg"))


        except Exception as e:
            pass

    new_urls = upload_multiple_images_to_firebase(image_urls)
    print(new_urls)
    for url in image_urls:
        os.remove(url)
    if new_urls is None or len(new_urls) == 0:
        new_urls = image_urls
    return new_urls


if __name__ == "__main__":
    query = input("Enter a search query: ")
    images = scrape_images(query)

    print("Found {} images for '{}'".format(len(images), query))
    for image in images:
        print(image)
