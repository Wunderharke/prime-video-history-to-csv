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

# List that is filled with strings of viewing activity
activity_list = []

# Initialising PhantomJS driver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# In your terminal window do a 'whereis chromedriver' to find the location of chromedriver and make sure the path below is correct.
driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options) # uncomment for ubuntu
# driver = webdriver.Chrome(service=Service("/usr/lib/chromium-browser/chromedriver"), options=chrome_options) 


def navigate_pages():
    """
    Navigates to the Viewing History page
    """
    print('Retrieving viewing activity...')

    scroll_to_bottom()
    expand_episodes_watched()
    get_page_activity()
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

def get_page_activity():
    """
    Gets all viewing activity on current page
    """

    # List that contains all row elements on viewing activity page
    row_list = driver.find_elements_by_xpath('//div[@data-automation-id="activity-history-items"]/ul/li')
    print(len(row_list))

    # Works to here

    # date
    # //div[@data-automation-id="activity-history-items"]/ul/li/div/div

    # show
    # //div[@data-automation-id="activity-history-items"]/ul/li/ul/li/div/div/div/div/a

    # episodes
    # //div[@data-automation-id="activity-history-items"]/ul/li/ul/li/div/ul/li/div/p
    # /ul/li/div/ul/li

    for row in row_list:
        print("################")

        eps = row.find_elements_by_xpath('./ul/li/div/ul/li/div/p')
        for ep in eps:
            date = row.find_element_by_xpath('./div/div')
            show = row.find_element_by_xpath('./ul/li/div/div/div/div/a')
            print(date.text + " " + show.text + " " + ep.text)
            activity_list.append(date.text + ", " + show.text + " " + ep.text + '\n')


def expand_episodes_watched():
    time.sleep(9)
    row_list = driver.find_elements_by_xpath('//div[@data-automation-id="activity-history-items"]//input[@type="checkbox"]')

    for row in row_list:
        time.sleep(0.4)
        driver.execute_script("arguments[0].scrollIntoView();", row)
        driver.execute_script("arguments[0].click();", row)


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

    navigate_pages()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='location of the folder with all your photos')
    parser.add_argument('password', help='where you want the photos moved to')
    args = parser.parse_args()

    try:
        main(args.username, args.password)
        exit(0)
    except Exception as e:
        print(e)
        exit(1)