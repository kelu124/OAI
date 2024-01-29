# linkedin

import selenium, pandas, trafilatura
import time 
import pandas as pd 
from selenium import webdriver 
from selenium.webdriver import Chrome
from chromedriver_py import binary_path # this will get you the path variable


def getURLcontent(URL):
    # Define the Chrome webdriver options
    print("1/3 - Starting headless")
    svc = webdriver.ChromeService(executable_path=binary_path)
    print(binary_path)
    options = webdriver.ChromeOptions() 
    options.add_argument("--headless") # Set the Chrome webdriver to run in headless mode for scalability
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    # By default, Selenium waits for all resources to download before taking actions.
    # However, we don't need it as the page is populated with dynamically generated JavaScript code.
    options.page_load_strategy = "none"

    # Pass the defined options objects to initialize the web driver 
    driver = Chrome(service=svc,options=options) 
    # Set an implicit wait of 5 seconds to allow time for elements to appear before throwing an exception
    driver.implicitly_wait(5)
    print("2/3 - Getting URL, 10s expected" )
    #url = "https://www.instacart.com/store/sprouts/collections/bread/872?guest=true" 
    driver.get(URL) 
    time.sleep(10)
    print("3/3 - Extracting text.")
    content = trafilatura.extract(driver.page_source)

    return content

