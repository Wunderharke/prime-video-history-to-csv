#!/usr/bin/python3

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
import codecs

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import time
import argparse
from datetime import datetime
from datetime import datetime, timedelta

# List that is filled with strings of viewing activity
activity_list = []

# Initialising PhantomJS driver
chrome_options = Options()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# In your terminal window do a 'whereis chromedriver' to find the location of chromedriver and make sure the path below is correct.
# driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options) # uncomment for ubuntu
driver = webdriver.Chrome(service=Service("/usr/lib/chromium-browser/chromedriver"), options=chrome_options) 

DAYS_WORTH_OF_HISTORY = None

def navigate_pages():
    """
    Navigates to the Viewing History page
    """
    print('Retrieving viewing activity...')

    scroll_to_bottom()
    expand_episodes_watched()
    output_activity(activity_list)


def scroll_to_bottom():
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def expand_episodes_watched():
    more_than_needed = False

    time.sleep(9)
    row_list = driver.find_elements_by_xpath('//div[@data-automation-id="activity-history-items"]//input[@type="checkbox"]')

    for row in row_list:
        time.sleep(0.4)
        driver.execute_script("arguments[0].scrollIntoView();", row)
        driver.execute_script("arguments[0].click();", row)

        if DAYS_WORTH_OF_HISTORY:
            row_list = driver.find_elements_by_xpath('//div[@data-automation-id="activity-history-items"]/ul/li')
            for row in row_list:
                eps = row.find_elements_by_xpath('./ul/li/div/ul/li/div/p')
                for ep in eps:
                    date = row.find_element_by_xpath('./div/div')
                    datetime_object = datetime.strptime(date.text, '%d %B %Y')
                    if DAYS_WORTH_OF_HISTORY:
                        time_between = datetime.now() - datetime_object
                        if time_between.days>DAYS_WORTH_OF_HISTORY:
                            more_than_needed = True
                            break
                    
                if more_than_needed:
                    break
            
            if more_than_needed:
                break

    """
    Gets all viewing activity on current page
    """
    # List that contains all row elements on viewing activity page
    row_list = driver.find_elements_by_xpath('//div[@data-automation-id="activity-history-items"]/ul/li')
    for row in row_list:
        print("################")

        eps = row.find_elements_by_xpath('./ul/li/div/ul/li/div/p')
        for ep in eps:
            date = row.find_element_by_xpath('./div/div')
            datetime_object = datetime.strptime(date.text, '%d %B %Y')
            if DAYS_WORTH_OF_HISTORY:
                time_between = datetime.now() - datetime_object
                if time_between.days>DAYS_WORTH_OF_HISTORY:
                    break
            date_string = datetime_object.strftime('%d/%m/%y')
            show = row.find_element_by_xpath('./ul/li/div/div/div/div/a')
            show_title = show.text.replace(",", "")
            ep_name = ep.text.replace(",", "")
            print(date_string + " " + show_title + " " + ep_name)
            activity_list.append(date_string + ", " + show_title + " " + ep_name + '\n')


def output_activity(activity_list):
    """
    Outputs viewing activity into 'SERVICE_activity.txt'
    """

    service = 'prime_video'

    print('Writing activity to \'%s_activity.txt\'' % service.lower())
    # Open output file
    file = codecs.open('%s_history.csv' % service.lower(), 'w+', encoding='utf8')
    # Write to file
    for item in activity_list:
        file.write(item)

    # Close output file
    file.close()
    print('Process finished')


def main(username, password):
    """
    Logs into Amazon
    """

    print('Logging into Amazon')

    driver.get("https://www.amazon.co.uk/gp/video/settings/watch-history?ref_=dv_auth_ret&")

    # Clearing email textbox and typing in user's email
    time.sleep(10)
    driver.find_element_by_id('ap_email').clear()
    driver.find_element_by_id('ap_email').send_keys(username)

    # Clicking on submit button
    driver.find_element_by_id('continue').click()

    # Clearing password textbox and typing in user's password
    time.sleep(10)
    driver.find_element_by_id('ap_password').clear()
    driver.find_element_by_id('ap_password').send_keys(password)

    # Clicking on submit button
    driver.find_element_by_id('signInSubmit').click()

    # Navigate to viewing activity page
    driver.get('https://www.amazon.co.uk/gp/video/settings/watch-history?ref_=dv_auth_ret&')

    # Do a check here if we're on the Watch History page or what.
    page_header_check = driver.find_elements_by_xpath('//div[@data-automation-id="activity-history-items"]//h3')
    if len(page_header_check) < 1:
        print("Not logged in properly")
        raise Exception
    
    navigate_pages()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', required=True, help='Your amazon prime video username')
    parser.add_argument('--password', required=True, help='Amazon password')
    parser.add_argument('--history', required=False, type=int, help='How many days worth of history do you want?')
    args = parser.parse_args()
    
    if args.history:
        DAYS_WORTH_OF_HISTORY = args.history

    main(args.username, args.password)