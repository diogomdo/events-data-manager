import datetime
import difflib
import time
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from webdriver_manager.firefox import GeckoDriverManager

from data import create_connection, select_games_from_team, insert_op_name, insert_result_game, get_op_team_name, \
    get_teams_with_games

op_team_name = ''
op_opponent_team_name = ''
initial_page_number = 1
match_result = ''


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
    # TODO correct link page with https://www.oddsportal.com/search/results/~~~~.koç/page/2/
    # probably error related with line 314
    url = get_current_url().split("/")
    url[-2] = str(1)
    return "/".join(url)


def search_box_operation(team):
    path_found = driver.find_element_by_xpath('//*[@id="search-match"]')
    path_found.click()
    path_found.send_keys(team)
    select = Select(driver.find_element_by_xpath('//*[@id="search-sport"]'))
    select.select_by_visible_text('Soccer')
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div['
                                 '1]/form/div/div/div/button/span/span').click()


def search_team(team_name="", team_id=""):
    try:
        global op_team_name
        r = get_op_team_name(team_id=team_id)
        n = r if r else team_name
        op_team_name = n
        index = len(n.split())-1

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
                index = index-1

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
            team_data = [item.text for item in row.find_elements_by_xpath(".//*[self::td or self::th]")]
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
        print('No results error')
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


def is_element(element):
    return op_team_name not in element


def extract_opponent(game):
    teams_list = game[1].replace(" - ", ",").split(",")
    r = list(filter(is_element, teams_list))
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
    next_page_link = driver.find_element_by_xpath(
        "/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div/div[2]/a[13]").get_attribute('href')
    driver.get(next_page_link)


def go_to_next_page(match_date, last_match_date):
    return True if match_date.date() < last_match_date.date() else False


def separator_has_year(separator_details):
    line = separator_details[0].replace("\n", " ")
    year = re.search(r"([0-9]{4})$", line)
    if year:
        return int(year[0])
    else:
        return False


def find_site_match_year(match_list):
    for element in reversed(match_list):
        r = [item.text for item in element.find_elements_by_xpath(".//*[self::td or self::th]")]
        if is_separator(r):
            year = separator_has_year(separator_details=r)
            if year:
                return year
            else:
                return datetime.datetime.now().year


def verify_team_match(team, match_date_time, opponent):
    while True:
        table_rows = driver.find_elements_by_xpath(
            '/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div/table/tbody/tr')

        page_last_game = [item.text for item in table_rows[-1].find_elements_by_xpath(".//*[self::td or self::th]")]
        last_game_date = datetime.datetime.strptime(page_last_game[0], "%d/%m, %H:%M")

        match_year = find_site_match_year(match_list=table_rows)
        last_game_date = last_game_date.replace(year=match_year)

        if go_to_next_page(match_date=match_date_time, last_match_date=last_game_date):
            check_next_page()
        else:
            for row in table_rows:
                game_data = [item.text for item in row.find_elements_by_xpath(".//*[self::td or self::th]")]
                if not is_separator(game_data):
                    op_match_date_time = datetime.datetime.strptime(game_data[0], "%d/%m, %H:%M")
                    op_match_date_time = op_match_date_time.replace(year=datetime.datetime.now().year)
                    if evaluate_date_match(match_date=match_date_time, op_match_date=op_match_date_time):
                        evaluate_game_match(game_data=game_data, opponent=opponent)
                        if match_result:
                            return True
                        else:
                            return False
            else:
                print("No match found for {} event.".format(game_data))
                return False


def save_data(team_id="", opponent_team_id="", game_id=""):
    """
    - Have loaded database
    - Save in Teams table the odds portal alias
    - Save in Games the match result
    """
    conn = create_connection("database/events-data.db")
    global op_opponent_team_name, op_team_name, match_result
    print("Data to save: Odds Portal alias '{}' - Opponent Odds Portal alias '{}' - result: '{}'".format(op_team_name,
                                                                                                         op_opponent_team_name,
                                                                                                         match_result))
    if op_team_name:
        insert_op_name(conn=conn, op_team_name=op_team_name, team_id=team_id)

    if op_opponent_team_name:
        insert_op_name(conn=conn, op_team_name=op_opponent_team_name, team_id=opponent_team_id)

    if match_result:
        insert_result_game(conn=conn, game_id=game_id, result=match_result)

    op_opponent_team_name = ""
    op_team_name = ""
    match_result = ""


def load_games():
    return get_teams_with_games()


def load_team_matches(team_id):
    conn = create_connection("database/events-data.db")

    with conn:
        return select_games_from_team(conn, team_id)


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

    """
    Game example
    e0b7e68b22ab499d83520626b85bcba7;Ranheim IL;2021-11-20 16:57:24.180527
    3318958f955c462ebb473ef29c193544;17:00:00;2021-06-22;e0b7e68b22ab499d83520626b85bcba7;5eb55cc10d6f4f33a8eab7e9f15e8036;;2021-11-20 16:57:24.180527
    # team = 'Ranheim IL'
    # date = '2021-06-22'
    # hour = '17:00:00'
    # opponent = 'Raufoss IL'
    country = ''
    """
    ranhiem_id = 'e0b7e68b22ab499d83520626b85bcba7'

    team_ids = get_teams_with_games()

    for match_id in team_ids:
        team_matches = load_team_matches(match_id[0])
        driver.get(link)
        for match in team_matches:
            match_date_time = datetime.datetime.strptime(", ".join([match["match_date"], match["match_time"]]),
                                                         "%Y-%m-%d, %H:%M:%S")
            if search_team(match["team_name"], match["team_id"]):
                print("OP team name: {}".format(op_team_name))
                if verify_team_match(match["team_name"], match_date_time, match["opponent_name"]):
                    save_data(game_id=match["game_id"], team_id=match["team_id"], opponent_team_id=match["opponent_id"])
            else:
                print("Run ended for team: {}".format(match["team_name"]))


scrape_search_result()
