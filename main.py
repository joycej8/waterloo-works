import time
import json
import pandas as pd
import logging
import openpyxl
from job_prioritization import sort_shortlisted_by_confidence
from job import Job
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

logging.getLogger().setLevel(logging.INFO)

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# Read appsettings.json and return credentials
def get_credentials():
    with open('appsettings.json', 'r') as file:
        settings = json.load(file)

    username = settings['credentials']['username']
    password = settings['credentials']['password']

    return username, password

# log into waterloo works with username and password
def login(username, password):
    url = 'https://waterlooworks.uwaterloo.ca/waterloo.htm?action=login'

    # login
    driver.get(url)
    driver.find_element(By.ID, "userNameInput").send_keys(username)
    driver.find_element(By.ID, "nextButton").click()
    driver.find_element(By.ID, "passwordInput").send_keys(password)
    driver.find_element(By.ID, "submitButton").click()

    # time to put in duo code for 2fa. #TODO: make it automatic if possible
    logging.info("Waiting for duo authentication to complete")
    time.sleep(15)

# get all jobs from all pages in Shortlist page
def get_shortlisted_info():
    # redirect to shortlist page
    coop_postings_url = 'https://waterlooworks.uwaterloo.ca/myAccount/co-op/full/jobs.htm'
    driver.get(coop_postings_url)

    shortlist_link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Shortlist")))
    shortlist_link.click()

    # get shortlist info
    shortlisted = []
    page_num = 1

    _get_shortlist_info(shortlisted)
    logging.info(f"Finished getting shortlisted jobs on page {page_num}")

    # if there exists pages to paginate, continue going through the pages
    can_pagination = _can_paginate()
    if can_pagination:
        is_next_enabled = driver.find_element(By.PARTIAL_LINK_TEXT, "»").find_element(By.XPATH, "..").get_attribute("class")

        # pagination to get rest of shortlist
        while "disabled" not in is_next_enabled:
            next_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "»")))
            page_num += 1
            driver.execute_script("window.scrollTo(0, 0);")
            next_button.click()
            time.sleep(1) # sleep so that next page can be loaded
            _get_shortlist_info(shortlisted)
            logging.info(f"Finished getting shortlisted jobs on page {page_num}")

            is_next_enabled = driver.find_element(By.PARTIAL_LINK_TEXT, "»").find_element(By.XPATH, "..").get_attribute("class")

    # order based on user preference
    shortlisted = sort_shortlisted_by_confidence(shortlisted)

    # insert jobs to excel
    _insert_to_excel(shortlisted)

# returns true if pagination is possible
def _can_paginate():
    try:
        driver.find_element(By.PARTIAL_LINK_TEXT, "»")
        return True
    except NoSuchElementException:
        return False 

# get all jobs on current Shortlist page
def _get_shortlist_info(shortlisted):
    # get shortlist info
    table = driver.find_element(By.ID, 'postingsTableDiv')
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    rows = tbody.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table
    shortlist_len = len(rows)

    for i in range(shortlist_len):
        row = rows[i]
        app_status = row.find_elements(By.TAG_NAME, "td")[1].accessible_name

        if app_status == "": # only get jobs I haven't applied to
            # get info from job in current row 
            company = row.find_elements(By.TAG_NAME, "td")[4].accessible_name
            title = row.find_elements(By.TAG_NAME, "td")[3].accessible_name
            status = row.find_elements(By.TAG_NAME, "td")[7].accessible_name
            application_num = int(row.find_elements(By.TAG_NAME, "td")[10].accessible_name)

            # Get detailed info through View button         
            view_dropdown = row.find_element(By.PARTIAL_LINK_TEXT, "View")
            view_dropdown.click()
            wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "new tab"))).click()
            driver.switch_to.window(driver.window_handles[1])

            # wait until page loads
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Job Posting Information']")))

            # Perform actions in the new tab 
            job = scrape_job(company, title, status, application_num)
            shortlisted.append(job)

            # Close the new tab and switch back to the original tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    return shortlisted

# get job info from page
def scrape_job(company, title, status, application_num):
    try:
        num_openings = int(_get_table_value('Job Openings:'))
        work_duration = _get_table_value('Work Term Duration:')
        location_arrangement = _get_table_value('Employment Location Arrangement:')
        location = f"{_get_table_value('City')}, {_get_table_value('Province/State:')}, {_get_table_value('Country:')}"
        description = _get_table_value('Job Summary:')
        responsibilities = _get_table_value('Job Responsibilities:')
        skills = _get_table_value('Required Skills:')
        pay = _get_table_value('Compensation and Benefits:')
        rating, num_rating, programs_hired, faculty_hired, work_term_hired = _get_ratings_and_hiring_history()

        # [company, title, status, applicates per position, work duration, location, location_arrangement, description, responsibilities, skills, pay, rating, num_rating]
        job = Job(company, title, status, application_num, num_openings, work_duration, location, location_arrangement, description, responsibilities, skills, pay, rating, num_rating, programs_hired, faculty_hired, work_term_hired)

        logging.info(f"Finished {company} {title}")
        return job
    
    except Exception as e:
        logging.error(f"Exception at {company} - {title}. {e}")

# get rating info
def _get_ratings_and_hiring_history():
    try:
        rating_element = driver.find_elements(By.XPATH, "//a[contains(text(), 'Work Term Ratings')]//span[@class='badge badge-info']")

        # Check if there is at least one <span> element
        if rating_element:
            wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Work Term Ratings"))).click()
            #wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Work Term Ratings Summary']"))) # wait until page loads
            time.sleep(0.3) # TODO: have a better fix
            rating = float(_get_table_value_with_index(2))
            num_ratings = int(_get_table_value_with_index(3))
            programs_hired = _get_most_freq_hired_programs()
            faculty_hired = _get_hire_by_faculty()
            work_term_hired = _get_hires_by_work_term()
            return rating, num_ratings, programs_hired, faculty_hired, work_term_hired
        else:
            return "", "", "", "", ""

    except Exception as e:
        logging.error(e)

def _get_hire_by_faculty():
    faculties = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='tspan'][contains(., 'Hires by Faculty')]/ancestor::*[name()='text']/following-sibling::*[contains(@class, 'highcharts-data-labels highcharts-tracker')]//*[name()='tspan'][contains(@style, 'font-weight:bold')]")
    percentages = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='tspan'][contains(., 'Hires by Faculty')]/ancestor::*[name()='text']/following-sibling::*[contains(@class, 'highcharts-data-labels highcharts-tracker')]//*[name()='tspan'][@dx='0']")

    faculty_names = [faculty.text for faculty in faculties if faculty.text]
    percentage_numbers = [int(percentage.text[2:-1])/100 for percentage in percentages if percentage.text]

    return dict(zip(faculty_names, percentage_numbers))

def _get_hires_by_work_term():
    work_terms = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='tspan'][contains(., 'Hires by Student Work Term Number')]/ancestor::*[name()='text']/following-sibling::*[contains(@class, 'highcharts-data-labels highcharts-tracker')]//*[name()='tspan'][contains(@style, 'font-weight:bold')]")
    percentages = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='tspan'][contains(., 'Hires by Student Work Term Number')]/ancestor::*[name()='text']/following-sibling::*[contains(@class, 'highcharts-data-labels highcharts-tracker')]//*[name()='tspan'][@dx='0']")

    work_term_names = [work_term.text for work_term in work_terms if work_term.text]
    percentage_numbers = [int(percentage.text[2:-1])/100 for percentage in percentages if percentage.text]

    return dict(zip(work_term_names, percentage_numbers))

def _get_most_freq_hired_programs():
    programs = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='tspan'][contains(., 'Most Frequently Hired Programs')]/ancestor::*[name()='text']/following-sibling::*[contains(@class, 'highcharts-axis-labels highcharts-xaxis-labels')]//*[name()='tspan']")
    hires = driver.find_elements(By.XPATH, "//*[name()='svg']//*[name()='tspan'][contains(., 'Most Frequently Hired Programs')]/ancestor::*[name()='text']/following-sibling::*[contains(@class, 'highcharts-data-labels highcharts-tracker')]//*[name()='tspan']")

    # Extracting text from selected elements
    program_names = [program.text for program in programs if program.text]
    hire_numbers = [int(hire.text) for hire in hires if hire.text]

    return dict(zip(program_names, hire_numbers))

# get value of job information given table key
def _get_table_value(key):
    try:
        xpath_expression = f"//td[contains(., '{key}')]"
        key_td = driver.find_elements(By.XPATH, xpath_expression)
        if key_td:
            return key_td[0].find_element(By.XPATH, "following-sibling::td").text
        else:
            return ""

    except Exception as e:
        logging.error(f"Exception on key {key}", e)

# get value of job information given table key
def _get_table_value_with_index(index):
    try:
        xpath_expression = f"(//table[@class='table table-bordered table-striped'])[2]//td[contains(., 'Employer Organization')]/following-sibling::td[{index}]"
        value = driver.find_elements(By.XPATH, xpath_expression)
        if value:
            return value[0].text
        else:
            return ""

    except Exception as e:
        logging.error(e)

# insert into excel
def _insert_to_excel(shortlisted):
    try:
        logging.info("Inserting shortlisted data info into excel")

        column_names = ["Compatibility", "Company", "Title", "Status", "Applicants Per Position", "Work Duration", "Location", "Location Arrangement", "Pay", "Rating", "Num Ratings", "Hires By Program", "Hires By Faculty", "Hires By Work Term", "Description", "Responsibilities", "Skills"]
        job_items = []

        # object to list
        for job in shortlisted:
            item = job.to_list()
            job_items.append(item)

        df = pd.DataFrame(job_items, columns=column_names)

        # Create a Pandas Excel writer using XlsxWriter as the engine
        file_name = "waterloo_works_shortlist_sorted.xlsx"
        sheet_name = 'Waterloo Works Shortlist'
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            max_width = 80

            for i, col in enumerate(df.columns):
                max_len = min(max(df[col].astype(str).apply(len).max(), len(col)), max_width)
                worksheet.column_dimensions[worksheet.cell(row=1, column=i+1).column_letter].width = max_len + 2
                worksheet.column_dimensions[worksheet.cell(row=1, column=i+1).column_letter].alignment = openpyxl.styles.Alignment(wrap_text=True)
        
        logging.info(f"Finished inserting shortlisted data info into {file_name}")

    except Exception as e:
        logging.error(f"{e}")

def main():
    try:
        username, password = get_credentials()
        login(username, password)
        get_shortlisted_info()
    except Exception as e:
        logging.error(f"Failed to get shortlisted info: Error {e}")

if __name__ == "__main__":
    main()