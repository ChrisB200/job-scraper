from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException
from bs4 import BeautifulSoup
from logger import Logger
import time
import json
import pgeocode

logger = Logger("info")

# Appends new content to old content
def update_json(filename, content):
    try:
        with open(filename, "r") as file:
            old_content = json.load(file)
    except:
        old_content = []

    for item in content:
        old_content.append(item)

    with open(filename, "w") as file:
        json.dump(old_content, file) 

# Checks if content of a tag is present
def check_presence(html, tag, messages):
    check = False
    for item in html.find_all(tag):
        for message in messages:
            if message in item.text:
                check = True
                break
    return check

# Returns the soup of a page
def return_soup(driver):
    innerHTML = driver.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(innerHTML, "lxml")
    return soup

# Returns latitude and longitude of postcode
def return_long_lat(postcode):
    country = pgeocode.Nominatim('gb')
    details = country.query_postal_code(postcode)
    return [details.latitude, details.longitude]

# Driver setup 
def create_driver():
    options = webdriver.ChromeOptions()
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    options.add_argument('user-agent={0}'.format(user_agent))
    options.add_argument("--headless")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("start-maximised")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)
    return driver

# Checks if a function has returned an error
def check_error(func):
    def wrapper(*args, **kwargs):
        item = func(*args, **kwargs)
        if item[0] < 0:
            print(item[1])
        else:
            return item[1]
    return wrapper

# Loads a page and returns the html content of the page
def load_page(driver, url, element, timeout=15):
    try:
        driver.get(url) 
        wait_until(driver, "presence", element, timeout)
        return return_soup(driver)
    except TimeoutException:
        logger.exception("Timeout while searching for element")
    except NoSuchElementException:
        logger.exception(f"Element with locator '{element[0]}' and locatorName '{element[1]}' not found on the page")
        

def test_wait(driver, condition, element, timeout=15):
    while True:
        if condition == "clickable":
            try:
                temp = driver.find_element(element[0], element[1])
                temp.click()
            except:
                pass
@check_error
def wait_until(driver, condition, element, timeout=15):
    try:
        element_locator = (element[0], element[1])
        if condition.lower() == "presence":
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located(element_locator))
        elif condition.lower() == "clickable":
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element_locator))

            if condition == "clickable":
                for i in range(3):
                    try:
                        temp_element = driver.find_element(element_locator[0], element_locator[1])
                        driver.execute_script("arguments[0].scrollIntoView();", temp_element)
                        time.sleep(1)
                        temp_element.click()
                        return 0, "Clicked"
                    except StaleElementReferenceException:
                        continue

            return -1, "Element is stale and cannot be clicked"
        if condition == "presence":
            return 0, "Element is currently present"
    except ElementNotInteractableException:
        return -1, "Element is currently not interactable"
    except NoSuchElementException:
        return -1, f"Element with locator '{element[0]}' and locatorName '{element[1]}' not found on the page"
    except TimeoutException:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element_locator))


    
# Splits the page numbers into current page and total pages
@check_error
def page_number(page, element, identifier):
    try:
        # Get the text from the page number element python
        page_text = page.find(element, identifier)
        text = page_text.text
        
        # Split the text to get the current page and total page number
        textSplit = text.split(" ")
        num1 = int(textSplit[1])
        num2 = int(textSplit[3])
    except:
        return -1, "Unable to find page"
    finally:
        return 0, [num1, num2]

# Interacts with filters by following an order
def click_order(driver, order, locator=None):
    for element_property in order:
        if locator is None:
            new_locator = [element_property[0], element_property[1]]
        else:
            new_locator = [locator, element_property]
        
        element = wait_until(driver, "clickable", new_locator)
        
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(3)

def click(driver, locator):
    element = wait_until(driver, "clickable", locator)

# Returns a property of a tag
def get_property(page, tag, prop):
    link = page.find(tag)
    return link.attrs[prop]

