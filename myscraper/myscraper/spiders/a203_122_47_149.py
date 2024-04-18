import time
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import json


class MySpider(scrapy.Spider):
    name = 'myspider'

    def start_requests(self):
        url = 'http://203.122.47.149:7999/'
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        # Initialize Selenium WebDriver
        options = Options()
        options.headless = True  # Uncomment if you don't need a browser UI
        driver = webdriver.Chrome(options=options)

        # Fetch the page
        driver.get(response.url)

        driver.implicitly_wait(20)
        time.sleep(3)

        original_window = driver.current_window_handle
        image_urls = []
        for subject_index in range(22,62):
            # Assuming the button can be uniquely identified by its text or an attribute
            link = driver.find_element(By.XPATH,'//*[@id="mainBodyContainer"]/section[2]/section/a[1]')  # Adjust XPath as needed
            link.click()

            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

            # Loop through until we find a new window handle
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    break

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="mainBodyContainer"]/section[1]/header/h2'))
            )
            
            previous_window = driver.current_window_handle
            # Locate the dropdown elements
            exam_dropdown = Select(driver.find_element(By.ID, 'exam_select'))
            year_dropdown = Select(driver.find_element(By.ID, 'exam_year'))
            month_dropdown = Select(driver.find_element(By.ID, 'exam_month'))
            subject_dropdown = Select(driver.find_element(By.ID, 'exam_paper'))
            language_dropdown = Select(driver.find_element(By.ID, 'exam_language'))

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="exam_select"]/option[2]'))
            )
            exam_dropdown.select_by_index(1)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="exam_year"]/option[2]'))
            )
            year_dropdown.select_by_index(1)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="exam_month"]/option[2]'))
            )
            month_dropdown.select_by_index(1)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="exam_paper"]/option[2]'))
            )
            # change this to get a different subject
            subject_dropdown.select_by_index(subject_index)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="exam_language"]/option[2]'))
            )
            language_dropdown.select_by_index(1)

            start_button = driver.find_element(By.ID, 'subBtn')
            start_button.click()

            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(3))

            # Loop through until we find a new window handle
            for window_handle in driver.window_handles:
                if window_handle != previous_window and window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    break

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="instructionSection"]/form/label'))
            )
            
            checkbox = driver.find_element(By.XPATH, '//*[@id="verify"]')
            checkbox.click()  # Ticks the checkbox

            # Locate and click the 'Proceed' button by its text
            proceed_button = driver.find_element(By.XPATH, '//*[@id="mainBtn"]')
            proceed_button.click()  

            # Gets the number
            element = driver.find_element(By.XPATH, '//*[@id="not_visited_p"]')
            # Retrieve the text content of the element
            text = element.text
            # Use a regular expression to extract the number from the text
            number_match = re.search(r'\d+', text)
            if number_match:
                number = number_match.group()  # This will be the number as a string
            number = int(number)

            subject_image_urls = []
            for i in range(0,number):
                time.sleep(1)
            
                # Start the loop to iterate through the questions
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="questionImageSection"]/img'))
                )
                image_element = driver.find_element(By.XPATH, '//*[@id="questionImageSection"]/img')
                image_url = image_element.get_attribute('src')
                
                # Complete the image URL if needed
                if not image_url.startswith(('http:', 'https:')):
                    from urllib.parse import urljoin
                    base_url = 'http://203.122.47.149:8000/'
                    image_url = urljoin(base_url, image_url)
                    image_urls.append(image_url)
                    subject_image_urls.append(image_url)
                else:
                    image_urls.append(image_url)
                    subject_image_urls.append(image_url)
            
                # Select an answer if required, for example, the first option
                answer_option = driver.find_element(By.XPATH, '//*[@id="leftSection"]/section[2]/form/div[1]/input')
                answer_option.click()
                time.sleep(3)
                # Click 'Save and Next' to go to the next question
                save_and_next_button = driver.find_element(By.XPATH,'//*[@id="saveNextBtn"]')
                save_and_next_button.click()

            with open('all_subjects.json', 'a', encoding='utf-8') as f:  # Open in append mode
                # If file is empty, write an opening bracket
                if f.tell() == 0:
                    f.write('[')
                else:  # Otherwise, write a comma before appending the next set of URLs
                    f.write(',')
                # Dump the current set of URLs as JSON without an enclosing bracket
                json.dump(subject_image_urls, f, ensure_ascii=False)
                f.write(']')

            driver.close()
            # Switch back to the new window
            driver.switch_to.window(previous_window)
            time.sleep(2)
            driver.close()
            driver.switch_to.window(original_window)
            time.sleep(2)

        driver.close()
        driver.quit()
        yield {'image_urls': image_urls}

        
