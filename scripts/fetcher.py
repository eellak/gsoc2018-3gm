#!/usr/bin/env python3

"""
Document Fetcher Module
The original code is taken from
https://github.com/arisp8/gazette-analysis/blob/master/mmu/automations/loader.py
Adhering to the GNU GPLv3 Licensing Terms
"""

import argparse
import time
from selenium import webdriver
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import ElementNotVisibleException
from bs4 import BeautifulSoup
import os
import errno
import glob
import os.path
import datetime
from http.client import RemoteDisconnected
import platform
import sys
sys.path.append('../src')
from helpers import Helper


def handle_download(download_page, params):
    """Original function"""

    global output_dir

    filename = params['issue_title'] + ".pdf"
    outfile = '{}/{}'.format(output_dir, filename)
    if os.path.isfile(outfile):
        return

    try:
        # First we get the redirect link from the download page
        html = Helper.get_url_contents(download_page)
        beautiful_soup = BeautifulSoup(html, "html.parser")
        meta = beautiful_soup.find("meta", {"http-equiv": "REFRESH"})
        download_link = meta['content'].replace("0;url=", "")

        # We do the same process twice because it involves 2 redirects.
        beautiful_soup = BeautifulSoup(
            Helper.get_url_contents(download_link), "html.parser")
        meta = beautiful_soup.find("meta", {"http-equiv": "REFRESH"})
        download_link = meta['content'].replace("0;url=", "")
    except RemoteDisconnected as e:
        print(e)
        return

    Helper.download(download_link, filename, output_dir)


def extract_download_links(html, issue_type):
    """Original Function"""

    beautiful_soup = BeautifulSoup(html, "html.parser")
    result_table = beautiful_soup.find("table", {"id": "result_table"})
    rows = result_table.find_all("tr")

    if result_table.find("ul", {"id": "sitenav"}):
        start_row = 2
        end_row = -1
    else:
        start_row = 1
        end_row = len(rows)

    # We ignore the first 2 rows if there's pagination or the first row if
    # there's not and the last one
    for row in rows[start_row:end_row]:
        cells = row.find_all("td")
        info_cell = cells[1].find("b")
        download_cell = cells[2].find_all("a")

        info_cell_text = info_cell.get_text()
        info_cell_text = ' '.join(info_cell_text.split())
        info_cell_parts = info_cell_text.split(" - ")

        issue_title = info_cell_text
        issue_date = info_cell_parts[1]
        issue_title_first = issue_title.split("-")[0]
        issue_number = re.search(
            pattern=r'\d+',
            string=issue_title_first).group(0)

        date_parts = issue_date.split(".")
        issue_unix_date = datetime.datetime(
            day=int(
                date_parts[0]), month=int(
                date_parts[1]), year=int(
                date_parts[2]))

        download_path = download_cell[1]['href'] if len(
            download_cell) > 1 else download_cell[0]['href']
        download_link = "http://www.et.gr" + download_path
        params = {
            "issue_title": issue_title,
            "issue_date": issue_unix_date,
            "issue_number": issue_number,
            "issue_type": issue_type}
        print('Download Link')
        print(download_link)
        handle_download(download_link, params)


if __name__ == '__main__':

    # Parse Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-date_from', help='Date from in DD.MM.YYYY format')
    parser.add_argument('-date_to', help='Date to in DD.MM.YYYY format')
    parser.add_argument('-output_dir', help='Output Directory')
    parser.add_argument('--chromedriver', help='Chrome driver executable')

    args = parser.parse_args()

    date_from = args.date_from
    date_to = args.date_to
    chromedriver_executable = args.chromedriver

    if not chromedriver_executable:
        print('Chrome driver not specified. Trying ./chromedriver')
        chromedriver_executable = './chromedriver'


    global output_dir
    output_dir = args.output_dir

    print(
        'Fetching Government Gazette Issues from {} to {}'.format(
            date_from,
            date_to))

    # Initialize Driver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    try:
        driver = webdriver.Chrome(chromedriver_executable, chrome_options=options)
    except:
        print('Could not find chromedriver')




    driver.get('http://www.et.gr/idocs-nph/search/fekForm.html')

    driver.find_element_by_name("showhide").click()

    # Enter Details
    driver.find_element_by_name("fekReleaseDateTo").clear()
    driver.find_element_by_name("fekReleaseDateTo").send_keys(date_to)
    driver.find_element_by_name("fekReleaseDateFrom").clear()
    driver.find_element_by_name("fekReleaseDateFrom").send_keys(date_from)

    driver.find_element_by_name("fekEffectiveDateTo").clear()
    driver.find_element_by_name("fekEffectiveDateTo").send_keys(date_to)
    driver.find_element_by_name("fekEffectiveDateFrom").clear()
    driver.find_element_by_name("fekEffectiveDateFrom").send_keys(date_from)

    driver.find_element_by_name("chbIssue_1").click()
    driver.find_element_by_id("search").click()

    try:
        # By default we'll see the first page of results, well.. first
        active_page = 1

        # Gets the pagination list items
        pages = driver.find_elements_by_class_name("pagination_field")
        # If there's no paginations then there's one page (max)
        num_pages = len(pages) if len(pages) else 1

        for current_page in range(0, num_pages):

            # Extract and handle download links.
            extract_download_links(driver.page_source, 'Α')

            # We have to re-find the pagination list because the DOM has been
            # rebuilt.
            pages = driver.find_elements_by_class_name("pagination_field")
            # Loads the next page of results
            if current_page + 1 < len(pages):
                pages[current_page + 1].click()
                time.sleep(1)

    except AttributeError:
        print('Could not find results')

    finally:
        driver.quit()
