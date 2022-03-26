import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from webdriver_manager.firefox import GeckoDriverManager

from extractor.data import get_teams_without_alias, insert_op_quick_link
from extractor.page import is_team_page, is_no_results_page, is_zero_results_page, select_team_page, get_current_url
from extractor.utils import get_main_team_name_by_common

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def resolve_quick_link() -> str:
    url_split_index = -2
    selected = Select(driver.find_element_by_xpath('//*[@id="search-sport"]')).first_selected_option.text
    if selected != "All sports":
        url_split_index = url_split_index - 1
    quick_link = get_current_url(driver=driver).split("/")[url_split_index]
    if ":" in quick_link:
        logging.info("Odds portal quick: '{}'".format(quick_link))
        return quick_link
    else:
        logging.warning("'{}' is not a valid quick link.".format(quick_link))
        return "N/A"


def evaluate_search_result(team_name, search_name):
    if is_team_page(driver=driver):
        return True
    elif is_no_results_page(driver=driver):
        return False
    elif is_zero_results_page(driver=driver):
        return False
    elif select_team_page(team=team_name, driver=driver, search_name=search_name):
        return True


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


def main():
    try:
        global driver

        options = Options()
        options.add_argument("--headless")
        options.add_argument('--window-size=1200,1024')
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        # webdriver.Firefox(options=options)

        logging.info("Teams crawler started.")
        link = 'https://www.oddsportal.com/results/#soccer'
        driver.get(link)
        time.sleep(5)

        teams = get_teams_without_alias()

        for team in teams:
            logging.info("placard team name: {}".format(team))
            search_box_operation(team=team.team_name, driver=driver)
            if evaluate_search_result(team_name=team.team_name, search_name=team.team_name):
                table_rows = driver.find_elements_by_xpath(
                    '/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div/table/tbody/tr')
                main_team_op_name = get_main_team_name_by_common(rows=table_rows[:10])
                quick_link = resolve_quick_link()
                logging.info("odds portal team name: {}".format(main_team_op_name))
            else:
                logging.warning("No results for {}".format(team.team_name))
                quick_link = "N/R"
            insert_op_quick_link(op_id=quick_link, team_id=team.team_id)
        driver.close()
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    main()
