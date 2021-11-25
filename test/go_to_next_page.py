from datetime import datetime


def go_to_next_page(match_date, last_match_date):
    if match_date.date() < last_match_date.date() and match_date.date().replace(year=1900) > datetime.now().replace(year=1900):
        return True
    else:
        return False