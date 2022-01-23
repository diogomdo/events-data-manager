import difflib
import re

from selenium.webdriver.support.select import Select

from extractor.utils import extract_row_details


def check_next_page(driver):
    pagination_section = driver.find_element_by_xpath("//*[@id='pagination']")
    next_page_url = pagination_section.find_elements_by_tag_name("a")[-2].get_attribute("href")
    driver.get(next_page_url)


def get_last_page(driver) -> int:
    pagination_section = driver.find_element_by_xpath("//*[@id='pagination']")
    last_page_url = pagination_section.find_elements_by_tag_name("a")[-1].get_attribute("href")
    last_page_number = last_page_url.split("/")[-2]
    return int(last_page_number)


def is_team_page(driver):
    try:
        result_search = driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div/div/ul/li[2]/strong/span').text
        return True if int(result_search.split()[-1].replace('(', '').replace(')', '')) > 0 else False

    except:
        print('Something went wrong in team page.')
        return False


def search_box_operation(driver, team):
    path_found = driver.find_element_by_xpath('//*[@id="search-match"]')
    if path_found.get_attribute('value'):
        path_found.clear()
    path_found.click()
    path_found.send_keys(team)
    select = Select(driver.find_element_by_xpath('//*[@id="search-sport"]'))
    select.select_by_visible_text('Soccer')
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div['
                                 '1]/form/div/div/div/button/span/span').click()


def get_current_url(driver):
    return driver.current_url


def team_match_results_first_page_url(driver):
    url = get_current_url(driver=driver).split("/")
    url[-2] = str(1)
    return "/".join(url)


def is_no_results_page(driver):
    try:
        if "Unfortunately" in driver.find_element_by_xpath('//*[@id="emptyMsg"]').text:
            search_box = driver.find_element_by_xpath('//*[@id="search-match"]')
            search_box.clear()
            return True
    except:
        return False


def is_zero_results_page(driver):
    try:
        archive_results = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div["
                                                       "2]/div[1]/div/div/ul/li[2]/strong/span").text
        r = re.search(r"^.*?\([^\d]*(\d+)[^\d]*\).*$", archive_results)
        if int(r[1]) == 0:
            search_box = driver.find_element_by_xpath('//*[@id="search-match"]')
            search_box.clear()
            return False
        else:
            print("Something went wrong in zero result page!")
    except:
        return False


def select_team_page(team, driver):
    try:
        table_rows = driver.find_elements_by_xpath('/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div['
                                                   '1]/div/table/tbody/tr')
        for row in table_rows:
            team_data = extract_row_details(row)
            # TODO the or condition checks the search term and the team name
            if difflib.SequenceMatcher(None, team_data[0], team).ratio() > 0.75 or team in team_data[0]:
                driver.get(row.find_element_by_xpath(".//*[self::a]").get_attribute("href"))
                return True
        return False
    except:
        print('Not selected!')
