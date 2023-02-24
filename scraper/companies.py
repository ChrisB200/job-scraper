import time
import json

from browsing import *
from logger import Logger

# The method that will parse the ASDA website
def parse_asda():
    logger = Logger("debug")
    driver = create_driver()
    root_url = "https://www.asda.jobs/vacancy/find/results/"
    
    # Loads main page and numbers
    main_page_identifier = [By.ID, "posBrowser_ResultsGrid_pageBlock"]
    load_page(driver, root_url, main_page_identifier)
    
    # Filter locators
    xfilt = {
        "Store Roles": [By.LINK_TEXT, 'Store Roles'],
        "Store Assistant": [By.PARTIAL_LINK_TEXT, 'Store Assistant'],
        "Part Time": [By.LINK_TEXT, 'Part-time'],
        "Job Type": [By.XPATH, '//*[@id="posBrowser_Filter_pageBlock"]/div/div[3]/div[1]/div[2]/div/div[1]/div[1]'],
        "Employment Type": [By.XPATH, '//*[@id="posBrowser_Filter_pageBlock"]/div/div[3]/div[1]/div[3]/div/div[1]'],
        "Job Category": [By.XPATH, '//*[@id="posBrowser_Filter_pageBlock"]/div/div[3]/div[1]/div[1]/div/div[1]/div[1]']
    }

    # The order that the xPaths will be pressed
    filter_pattern = [xfilt["Store Roles"], xfilt["Job Category"], xfilt["Job Type"], xfilt["Store Assistant"], xfilt["Employment Type"], xfilt["Part Time"]]
    click_order(driver, filter_pattern)
    logger.debug("Asda filters clicked")
    
    # Main page updated with filters
    soup = return_soup(driver)
    time.sleep(3)

    # Gets page numbers
    page_numbers = page_number(soup, "div", {"class": "pagingText"})
    logger.debug("Asda page numbers collected")

    # Jobs that under 18 year olds can't do
    over18 = [
        "online service colleague - days ",
        "online service colleague - nights ",
        "petrol assistant  ",
        "security guard ",
        "security ",
        "store assistant - pharmacy  "
        ]

    # Scrolls through the pages and saves the links of each job posting
    links = []        
    for i in range(1, page_numbers[1]):
        logger.debug(f"Asda current page number = {i}")

        # Get page results
        next_page = driver.find_element(By.XPATH, '//*[@id="form_posBrowser_ResultsGrid"]/div/div[1]/div[3]/div[2]/a[2]')
        page = return_soup(driver)
        
        # Gets all links on page
        page_links = page.find_all("div", {"class": "rowLabel"})
        for link in page_links:
            temp = link.find("a")
            if temp.text.lower() not in over18:
                href = temp["href"]
                links.append(f"https://www.asda.jobs/{href}")

        # Goes onto next page 
        next_page.click()
        time.sleep(1)

    # Messages that mean that under 18s can't do the role
    messages = ["If the shifts for this role cover hours between midnight and 5am, you will need to be at least 18 years of age.",
                    "To be employed in this role you must be over the age of 18.",
                    "To be employed in this role you must be over the age of 18 and pass a basic level safeguarding check.",
                    "To be employed in this role you must be over the age of 18",
                    "To be employed in this role you must be over the age of 18 and pass an enhanced safeguarding check.",
                    "the age of 18",
                    "If the shifts for this role cover hours",
                    "Please note in addition to the advertised hourly rate, a further £2.54 nightshift premium"]
        
    # Gathers Job listing information from each link
    job_listings = []
    logger.debug("Finished collecting links off page")
    logger.debug("About to scrape all links")
    for i, link in enumerate(links):
        # Window Handling
        driver.execute_script(f'''window.open("{link}","_blank");''')
        driver.close()
        window_name = driver.window_handles[-1]
        driver.switch_to.window(window_name=window_name)
        
        # Loads the job listing page
        job_listing_identifier = [By.CLASS_NAME, "jobSumLabel"]
        job_listing_html = load_page(driver, link, job_listing_identifier)
        
        # Checks if the job posting is age 16 and above
        age_check = check_presence(job_listing_html, "span", messages)
        if age_check == False:
            # Gets values and labels
            job_listing = job_listing_html.find("ul", {"class": "jobSum"})
            job_listings_labels = job_listing.find_all("div", {"class": "jobSumLabel"})
            job_listings_values = job_listing.find_all("div", {"class": "jobSumValue"})

            click(driver, [By.CLASS_NAME, "miniMapButton"])
            driver.execute_script("window.scrollTo(0, 0);")

            # Calculates longitude and latitude
            map_page = return_soup(driver)
            postcode = map_page.find("div", {"class": "locationAddress"}).text.split(",")[-1]
            long_lat = return_long_lat(postcode)

            # Enters data not on the page
            job_listings_dict = {}
            job_listings_dict["Company"] = "Asda"
            job_listings_dict["Link"] = link
            job_listings_dict["Postcode"] = postcode
            job_listings_dict["Latitude"] = f"{long_lat[0]}"
            job_listings_dict["Longitude"] = f"{long_lat[1]}"

            # Gets job id
            ref = map_page.find("p", {"class": "p-jobref"})
            job_listings_dict["Id"] = ref.find("span").text

            # Chooses the labels that I want
            for i in range(0, len(job_listings_labels)):
                if job_listings_labels[i].text.lower() == "salary":
                    job_listings_dict[job_listings_labels[i].text] = job_listings_values[i].text.replace("\u00a3", "£")
                elif job_listings_labels[i].text.lower() not in ["category", "shift pattern", "closing date"]:
                    job_listings_dict[job_listings_labels[i].text] = job_listings_values[i].text
            
            # Checks if all fields are entered correctly
            if job_listings_dict["Latitude"].lower() != "nan" and job_listings_dict["Longitude"].lower() != "nan":
                job_listings.append(job_listings_dict)
                logger.debug(f"Successfully appended link: {link}")
            else:
                logger.debug(f"Unsuccessfully appended link {link}")

        driver.switch_to.window(window_name=window_name)

    # Updates JSON
    logger.debug("Successfully gathered all data from links")
    logger.debug("Putting links in JSON")
    update_json("listings.json", job_listings)
    logger.info("Successfully parsed: ASDA")

companies_list = [parse_asda]