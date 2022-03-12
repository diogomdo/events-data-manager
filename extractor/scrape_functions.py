import logging
import time
from typing import Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from webdriver_manager.firefox import GeckoDriverManager

from data import select_games_from_team, insert_op_name, insert_result_game, get_op_team_name, get_teams_with_games, \
    get_op_id, insert_op_quick_link
from extractor.db_element import DB_Element
from extractor.op_element import OP_Element, Element_Type
from extractor.page import check_next_page, get_last_page, is_team_page, search_box_operation, is_no_results_page, \
    is_zero_results_page, team_match_results_first_page_url, select_team_page, get_current_url
from extractor.utils import extract_row_details

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

op_team_name = ''
op_opponent_team_name = ''
initial_page_number = 1
match_result = ''


class NoMatchFound(Exception):
    logging.warning("No match was found for this event!")
    pass


class NoQuickLink(Exception):
    logging.warning("No quick link for this team!")
    pass


def evaluate_search_result(team_name, search_name):
    if is_team_page(driver=driver):
        return True
    elif is_no_results_page(driver=driver):
        return False
    elif is_zero_results_page(driver=driver):
        return False
    elif select_team_page(team=team_name, driver=driver, search_name=search_name):
        return True


def search_team(team_name: str, team_id: str):
    try:
        r = get_op_team_name(team_id=team_id)
        n = r if r else team_name
        index = len(n.split()) - 1

        # TODO Refactor team search trials
        # if team len > 1
        # First loop removal the last string from team name until len == 0
        # skip search if has just one element and string len <= 3
        # Second loop removel the first string from team name until len == 0
        # skip search if has just one element and string len <= 3
        while n:
            if is_team_page(driver):
                driver.get(team_match_results_first_page_url(driver=webdriver))
                return True

            search_box_operation(team=n, driver=driver)
            if evaluate_search_result(team_name=n, search_name=team_name):
                return True
            else:
                n = n.split()[index]
                index = index - 1

        logging.warning("Nothing else to do with this team.")
        return False
    except:
        logging.warning('Team "{}" with id: "{}" not found in odds portal search!'.format(team_name, team_id))
        return False


def is_element_in_cache(element):
    return next(filter(lambda x: element == x, cached_op_results), False)


def event_has_correspondence(match: DB_Element) -> Union[OP_Element, bool]:
    for op_match in cached_op_results:
        if match.match_date_time == op_match.date:
            logging.info("Date matched '{}' for event: {}".format(op_match.date, op_match.teams))
            return op_match
    else:
        return False


def navigator_stopper(match_date):
    if cached_op_results:
        if cached_op_results[-1].date < match_date:
            raise NoMatchFound


def solve_main_team_alias(table: list, main_team_name: str) -> str:
    # Add mechanism to check the main team alias within couple rows to certify the alias.
    # can be 3 or 4 match rows, but it raise the separator problem.

    # get game row with both teams
    # get entries with bold tag
    # infer which one has bold
    # if both then check the one with similar name
    # verify if the names with bold tag have more words on the right(already blindly adding) or in the left(beginning)
    name = ""
    home_team = ""
    visitor_team = ""
    bold_teams = []
    teams_match = table[1].find_elements_by_css_selector("td[class='name table-participant']")[0].text
    teams_list = teams_match.split(" - ")

    for t in table[1].find_elements_by_css_selector("span[class='bold']"):
        bold_teams.append(t.text)

    if len(bold_teams) == 0:
        raise Exception
    elif len(bold_teams) == 1:
        for i, team in enumerate(teams_list):
            if bold_teams[0] in team:
                home_team = teams_list[i]
                visitor_team = teams_list[abs(i - 1)]
    else:
        for team in teams_list:
            initials = [x[0] for x in bold_teams]
            if any(init in team for init in initials):
                logging.info("Odds portal team alias: '{}' for '{}'.".format(team, main_team_name))

    for e in table[1].find_elements_by_css_selector("span[class='bold']"):
        name = name + " " + e.text
    return name


def navigator_page(match: DB_Element) -> Union[OP_Element, bool]:
    result_match = True
    page: int = 1
    last_page_number: int = get_last_page(driver=driver)
    while result_match:
        if page > last_page_number:
            raise NoMatchFound

        table_rows = driver.find_elements_by_xpath(
            '/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div/table/tbody/tr')

        # solve main team alias
        main_team_op_name = solve_main_team_alias(table=table_rows, main_team_name=match.main_team_name)

        for row in table_rows:
            element = OP_Element(element_details=extract_row_details(row), main_team=main_team_op_name.strip(),
                                 page=page)
            if element.type is not Element_Type.SEPARATOR:
                if not is_element_in_cache(element):
                    cached_op_results.append(element)
        else:
            is_match = event_has_correspondence(match=match)
            if isinstance(is_match, OP_Element):
                return is_match
            else:
                navigator_stopper(match_date=match.match_date_time)
                page = page + 1
                check_next_page(driver=driver)
    return False


def save_data(db_match: DB_Element, op_match: OP_Element = None):
    logging.info("Result game id: '{}' with teams: '{}' with result {}".format(db_match.game_id, op_match.teams,
                                                                               op_match.result))
    if op_match.main_team_name and op_match.opposition_name and op_match.result:
        insert_op_name(op_team_name=op_match.main_team_name, team_id=db_match.main_team_id)
        insert_op_name(op_team_name=op_match.opposition_name, team_id=db_match.opponent_id)
        insert_result_game(game_id=db_match.game_id, result=op_match.result)
        logging.info("Saved with success!")


def load_games():
    return get_teams_with_games()


def load_team_matches(team_id):
    return select_games_from_team(team_id)


def save_team_quick_link(team_id, quick_link):
    insert_op_quick_link(team_id, quick_link)


def by_quick_link(match: DB_Element) -> bool:
    logging.info("Accessing team '{}' with id '{}' page by quicklink.".format(match.main_team_name, match.main_team_id))
    op_id = get_op_id(team_id=match.main_team_id)
    if not op_id:
        raise NoQuickLink

    logging.info("Quicklink: '{}'".format(op_id))
    link = "https://www.oddsportal.com/search/results/" + op_id + "/"
    if ":" not in op_id:
        link = link + "soccer/"

    driver.get(link)

    if is_team_page(driver=driver):
        logging.info("Accessed with success!")

        result = navigator_page(match=match)
        if result:
            save_data(db_match=match, op_match=result)
            return True
    else:
        raise NoQuickLink


def resolve_quick_link() -> str:
    url_split_index = -2
    selected = Select(driver.find_element_by_xpath('//*[@id="search-sport"]')).first_selected_option.text
    if selected != "All sports":
        url_split_index = url_split_index - 1
    quick_link = get_current_url(driver=driver).split("/")[url_split_index]
    return quick_link


def by_search_box(match: DB_Element) -> bool:
    if search_team(team_name=match.main_team_name, team_id=match.main_team_id):
        logging.info("In team page.")

        # TODO Adjust the quick link scrap. Index may vary with the kind of quick link in url
        quick_link = resolve_quick_link()
        save_team_quick_link(team_id=match.main_team_id, quick_link=quick_link)

        result = navigator_page(match=match)
        if result:
            save_data(db_match=match, op_match=result)
            return True
    else:
        logging.warning("Run ended for team: {}".format(match.main_team_name))
        return False


def verify_in_cached_results(match: DB_Element) -> bool:
    op_match = event_has_correspondence(match=match)
    # The op team names should be solved at this point. Either by quick link or search box, once the cached results
    # has data, it means op team names aka alias should be solved and saved.
    # home_team_name = driver.find_element_by_xpath("//*[@id='search-match']").get_attribute("value")
    if op_match:
        save_data(db_match=match, op_match=op_match)
        return True


def scrape_search_result():
    global driver
    global cached_op_results

    options = Options()
    options.add_argument("--headless")
    options.add_argument('--window-size=1200,1024')
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    # webdriver.Firefox(options=options)

    logging.info("Scrape results started!")
    link = 'https://www.oddsportal.com/results/#soccer'
    driver.get(link)
    time.sleep(5)

    team_ids = get_teams_with_games()

    for match_id in team_ids:
        logging.info("Total number of teams to scrap: '{}'.".format(len(team_ids)))
        team_matches = load_team_matches(match_id[0])
        driver.get(link)

        cached_op_results = []
        logging.info("Start scrape for team id '{}' with '{}' matches.".format(match_id[0], len(team_matches)))
        for match in team_matches:
            if cached_op_results:
                if verify_in_cached_results(match=match):
                    continue
            try:
                if by_quick_link(match=match):
                    continue
            except NoMatchFound:
                continue
            except NoQuickLink:
                pass

            if by_search_box(match=match):
                continue
            else:
                break


scrape_search_result()
