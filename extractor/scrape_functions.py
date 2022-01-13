import datetime
import difflib
import re
import time
from typing import Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from webdriver_manager.firefox import GeckoDriverManager

from data import select_games_from_team, insert_op_name, insert_result_game, get_op_team_name, get_teams_with_games, \
    get_op_id
# Globals
from extractor.db_element import DB_Element
from extractor.op_element import OP_Element, Element_Type, cached_op_results

op_team_name = ''
op_opponent_team_name = ''
initial_page_number = 1
match_result = ''


class NoMatchFound(Exception):
    pass


class NoQuickLink(Exception):
    print("No quick link for this team!")
    pass


def is_zero_results_page():
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


def is_no_results_page():
    try:
        if "Unfortunately" in driver.find_element_by_xpath('//*[@id="emptyMsg"]').text:
            search_box = driver.find_element_by_xpath('//*[@id="search-match"]')
            search_box.clear()
            return True
    except:
        return False


def extract_row_details(r):
    return [item.text for item in r.find_elements_by_xpath(".//*[self::td or self::th]")]


def evaluate_search_result(team_name):
    if is_team_page():
        return True
    elif is_no_results_page():
        return False
    elif is_zero_results_page():
        return False
    elif select_team_page(team=team_name):
        return True


def get_current_url():
    return driver.current_url


def team_match_results_first_page_url():
    url = get_current_url().split("/")
    url[-2] = str(1)
    return "/".join(url)

    """
    TODO some teams are not found by the main search box, this can be tackled in two ways
    - evaluate if team table has the unique odds portal url id, and if so navigate directly to team page by building 
    url with that unique id. This must be analyzed at line 313
    
    - develop a selenium operation to search the team name in the secondary search box. This needs a new xpaths and 
    behavior expectation. This search must be done before or after the result of search_box_operation().
    """


def search_box_operation(team):
    path_found = driver.find_element_by_xpath('//*[@id="search-match"]')
    path_found.click()
    path_found.send_keys(team)
    select = Select(driver.find_element_by_xpath('//*[@id="search-sport"]'))
    select.select_by_visible_text('Soccer')
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div['
                                 '1]/form/div/div/div/button/span/span').click()


def search_team(team_name: str, team_id: str):
    try:
        global op_team_name
        r = get_op_team_name(team_id=team_id)
        n = r if r else team_name
        op_team_name = n
        index = len(n.split()) - 1

        while n:
            if is_team_page():
                driver.get(team_match_results_first_page_url())
                return True

            search_box_operation(team=n)
            if evaluate_search_result(team_name=n):
                op_team_name = n
                return True
            else:
                n = n.split()[index]
                index = index - 1

        print("Nothing else to do with this team.")
        return False
    except:
        print('Team not found!')
        return False


def select_team_page(team):
    try:
        table_rows = driver.find_elements_by_xpath('/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div['
                                                   '1]/div/table/tbody/tr')
        for row in table_rows:
            team_data = extract_row_details(row)
            # TODO the or condition checks the search term and the team name
            if team_data[0] == team or team_data[0] == op_team_name:
                driver.get(row.find_element_by_xpath(".//*[self::a]").get_attribute("href"))
                return True
        return False
    except:
        print('Not selected!')


def is_team_page():
    try:
        result_search = driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div/div/ul/li[2]/strong/span').text

        return True if int(result_search.split()[-1].replace('(', '').replace(')', '')) > 0 else False

    except:
        print('Something went wrong in team page.')
        return False


def is_separator(game_data):
    return True if "Soccer" in game_data[0] else False


def evaluate_date_match(match_date, op_match_date):
    # TODO evaluate time like at go_to_next_page()
    return True if match_date.day == op_match_date.day \
                   and match_date.month == op_match_date.month \
                   and match_date.hour == op_match_date.hour \
                   and match_date.minute == op_match_date.minute else False


def get_opponent_name(op_opponent, pl_opponent):
    global op_opponent_team_name
    result = difflib.SequenceMatcher(None, op_opponent, pl_opponent).ratio()

    if result >= 0.4:
        op_opponent_team_name = op_opponent
        return True


def extract_opponent(game, main_team=""):
    teams_list: list = []
    if isinstance(game, list):
        teams_list = game[1].replace(" - ", ",").split(",")
    elif isinstance(game, str):
        teams_list = game.replace(" - ", ",").split(",")

    r = list(filter(lambda element: element != main_team, teams_list))
    # r = list(filter(lambda element: is_element(element, main_team), teams_list))
    # r = list(filter(is_element, teams_list))
    return r[0].strip()


def extract_result(game):
    result = game[2].split(":")
    if result[0] == result[1]:
        return "W"
    else:
        return "L"


def evaluate_game_match(game_data, opponent):
    op_opponent = extract_opponent(game=game_data)

    if get_opponent_name(op_opponent=op_opponent, pl_opponent=opponent):
        print("Success!")
        global match_result
        match_result = extract_result(game_data)
        print("Game result: {}".format(match_result))
        return True


def check_next_page():
    # TODO add generic page changer
    next_page_link = driver.find_element_by_xpath(
        "/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div/div[2]/a[8]").get_attribute('href')

    driver.get(next_page_link)


def go_to_next_page(match_date, last_match_date):
    return True if match_date.date() < last_match_date.date() else False


def separator_has_year_regex(separator_details):
    line = separator_details[0].replace("\n", " ")
    year = re.findall(r"[0-9]{4}", line)
    if year:
        return year
    else:
        return False


def season_year(year_interval, match_data):
    curr_date = datetime.datetime.now().date()
    match_date = datetime.datetime.strptime(match_data[0], "%d/%m, %H:%M").date().replace(year=curr_date.year)

    if curr_date > match_date:
        year = curr_date.year
    else:
        year = year_interval[0]

    return int(year)


def evaluate_separator_year(separator, following_match=None):
    year: list = []
    year_res: int = 0

    if following_match is None:
        following_match = []
    if is_separator(separator):
        year = separator_has_year_regex(separator_details=separator)
        """
        evaluate 
        if has 2020/2021 this type of description then
            it has get if is 2020 or 2021, this can be achieved by comparing the following match data in following_match
            with that date compare with current day and month. If is prior it means the the older year eg. 2020, 
            otherwise is the later 2021.
        if the result from separator is single year, that is the match year.
        if none is the current year.
        
        :return must be a integer with year
        """

        if year is None or year is False:
            year_res = datetime.datetime.now().year
        elif len(year) == 1:
            year_res = int(year[0])
        elif len(year) > 1:  # TODO evaluate regex result if is the type xxxx/yyyy
            year_res = season_year(year_interval=year, match_data=following_match)
        else:
            raise ValueError(
                "Could not resolve the concrete match year. For match {} and separator year {}.".format(match_result,
                                                                                                        separator))

        return year_res
    else:
        print("Something went wrong with result of regex input: {}".format(separator))


def find_site_match_year(match_list):
    for i, element in enumerate(reversed(match_list)):
        r = extract_row_details(element)
        if is_separator(r):
            return evaluate_separator_year(separator=r,
                                           following_match=extract_row_details(match_list[-1]))


def calculate_match_date(date: datetime) -> datetime:
    match_date: datetime = None
    now = datetime.datetime.now()

    return match_date


def is_element_in_cache(element):
    return next(filter(lambda x: element == x, cached_op_results), False)


def event_has_correspondence(match: DB_Element) -> Union[OP_Element, bool]:
    for op_match in cached_op_results:
        if difflib.SequenceMatcher(None, match.main_team_name, op_match.teams).ratio() > 0.4 and \
                difflib.SequenceMatcher(None, match.opponent_name, op_match.teams).ratio() > 0.4 and \
                match.match_date_time == op_match.date:
            return op_match
    else:
        return False


def get_last_page() -> int:
    last_page = driver.find_element_by_xpath(
        "/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div/div[2]/a[9]").get_attribute("x-page")
    return int(last_page)


def navigator_page(match: DB_Element) -> Union[OP_Element, bool]:
    result_match = True
    page: int = 1
    last_page_number: int = get_last_page()
    while result_match :
        # TODO Add condition to skip match if all pages are covered but without any result
        if page > last_page_number:
            raise NoMatchFound
        table_rows = driver.find_elements_by_xpath(
            '/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div/table/tbody/tr')
        for row in table_rows:
            element = OP_Element(element_details=extract_row_details(row), page=page)
            if element.type is not Element_Type.SEPARATOR:
                # Add to cache pool
                if not is_element_in_cache(element):
                    cached_op_results.append(element)
        else:
            is_match = event_has_correspondence(match=match)
            if isinstance(is_match, OP_Element):
                return is_match
            else:
                page = page + 1
                check_next_page()
    return False


def verify_team_match(match: DB_Element):
    while True:
        table_rows = driver.find_elements_by_xpath(
            '/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div/table/tbody/tr')

        page_last_game = extract_row_details(table_rows[-1])
        last_game_date = datetime.datetime.strptime(page_last_game[0], "%d/%m, %H:%M")

        match_year = find_site_match_year(match_list=table_rows)
        last_game_date = last_game_date.replace(year=match_year)

        if go_to_next_page(match_date=match.match_date_time, last_match_date=last_game_date):
            # IMPORTANT the match year from the last match page must be persisted for the next match in the next page
            # until a new separator is detected
            check_next_page()
        else:
            for row in table_rows:
                game_data = extract_row_details(row)

                # TODO This date must be checked in the separator directly above of match row
                # change is_separator() function so save year while looping through events
                if is_separator(game_data=game_data):
                    match_year = evaluate_separator_year(separator=game_data)
                if not is_separator(game_data):
                    op_match_date_time = datetime.datetime.strptime(game_data[0], "%d/%m, %H:%M")

                    op_match_date_time = op_match_date_time.replace(year=match_year)
                    if evaluate_date_match(match_date=match.match_date_time, op_match_date=op_match_date_time):
                        evaluate_game_match(game_data=game_data, opponent=match.opponent_name)
                        if match_result:
                            return True
                        else:
                            return False
            else:
                print("No match found for {} event.".format(game_data))
                return False


def save_data(db_match: DB_Element, op_match: OP_Element = None):
    global op_opponent_team_name, op_team_name, match_result

    setattr(op_match, "opposition_name", extract_opponent(game=op_match.teams, main_team=op_match.main_team_name))

    if op_match.main_team_name and op_match.opposition_name and op_match.result:
        insert_op_name(op_team_name=op_match.main_team_name, team_id=db_match.main_team_id)
        insert_op_name(op_team_name=op_match.opposition_name, team_id=db_match.opponent_id)
        insert_result_game(game_id=db_match.game_id, result=match_result)


def load_games():
    return get_teams_with_games()


def load_team_matches(team_id):
    return select_games_from_team(team_id)


def by_quick_link(match: DB_Element) -> bool:
    op_id = get_op_id(team_id=match.main_team_id)
    if not op_id:
        raise NoQuickLink

    link = "https://www.oddsportal.com/search/results/" + op_id + "/"
    driver.get(link)

    if is_team_page():
        print("In team page.")
        home_team_name = driver.find_element_by_xpath("//*[@id='search-match']").get_attribute("value")

        result = navigator_page(match=match)
        if result:
            setattr(result, "main_team_name", home_team_name)
            save_data(db_match=match, op_match=result)
            return True
    else:
        print("Quick link not sufficient.")
        return False


def by_search_box(match: DB_Element) -> bool:
    if search_team(team_name=match.main_team_name, team_id=match.main_team_id):
        print("OP team name: {}".format(op_team_name))
        if verify_team_match(match=match):
            save_data(db_match=match)
            return True
    else:
        print("Run ended for team: {}".format(match["team_name"]))
        return False


def verify_in_cached_results(match: DB_Element) -> bool:
    op_match = event_has_correspondence(match=match)
    home_team_name = driver.find_element_by_xpath("//*[@id='search-match']").get_attribute("value")
    setattr(op_match, "main_team_name", home_team_name)
    if op_match:
        save_data(db_match=match, op_match=op_match)
        return True


def scrape_search_result():
    global driver

    options = Options()
    options.add_argument("--headless")
    options.add_argument('--window-size=1200,1024')
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    # webdriver.Firefox(options=options)

    link = 'https://www.oddsportal.com/results/#soccer'
    driver.get(link)
    time.sleep(5)

    team_ids = get_teams_with_games()

    for match_id in team_ids:
        team_matches = load_team_matches(match_id[0])
        driver.get(link)

        cached_op_results = []

        for match in team_matches:
            if cached_op_results:
                if verify_in_cached_results(match=match):
                    continue
            try:
                if by_quick_link(match=match):
                    continue
            except NoMatchFound:
                print("No match was found for this event!")
                continue
            except NoQuickLink:
                pass

            if by_search_box(match=match):
                continue


scrape_search_result()
