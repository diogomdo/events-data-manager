import unittest
from datetime import datetime

from evaluate_name import evaluate_opponent
from go_to_next_page import go_to_next_page


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here
        # self.assertTrue(evaluate_opponent("Ranheim", "Ranheim Il"))
        # self.assertTrue(evaluate_opponent("KFUM Oslo", "KFUM"))
        # self.assertTrue(evaluate_opponent("Sogndal", "Sogndal"))
        self.assertTrue(evaluate_opponent("Ull/Kisa", "Ullensaker/Kisa"))

    def test_date(self):
        last_game_date = datetime.strptime("25/07, 17:00", "%d/%m, %H:%M")
        last_game_date = last_game_date.replace(year=datetime.now().year)
        match_date = datetime.strptime("05/07, 17:00", "%d/%m, %H:%M")
        match_date = match_date.replace(year=datetime.now().year)
        self.assertTrue(go_to_next_page(last_match_date=last_game_date, match_date=match_date))

    def test_date2(self):
        last_game_date = datetime.strptime("25/07, 17:00", "%d/%m, %H:%M")
        last_game_date = last_game_date.replace(year=datetime.now().year)
        match_date = datetime.strptime("23/08, 17:00", "%d/%m, %H:%M")
        match_date = match_date.replace(year=datetime.now().year)
        self.assertFalse(go_to_next_page(last_match_date=last_game_date, match_date=match_date))

    def test_date3(self):
        last_game_date = datetime.strptime("25/07, 17:00", "%d/%m, %H:%M")
        last_game_date = last_game_date.replace(year=datetime.now().year)
        match_date = datetime.strptime("13/12, 17:00", "%d/%m, %H:%M")
        match_date = match_date.replace(year=datetime.now().year)
        self.assertTrue(go_to_next_page(last_match_date=last_game_date, match_date=match_date))

    def test_date4(self):
        last_game_date = datetime.strptime("25/07, 17:00", "%d/%m, %H:%M")
        last_game_date = last_game_date.replace(year=datetime.now().year)
        match_date = datetime.strptime("25/07, 17:00", "%d/%m, %H:%M")
        match_date = match_date.replace(year=datetime.now().year)
        self.assertFalse(go_to_next_page(last_match_date=last_game_date, match_date=match_date))

    def test_date5(self):
        last_game_date = datetime.strptime("25/07, 17:00", "%d/%m, %H:%M")
        last_game_date = last_game_date.replace(year=datetime.now().year)
        match_date = datetime.strptime("26/07, 17:00", "%d/%m, %H:%M")
        match_date = match_date.replace(year=datetime.now().year)
        self.assertFalse(go_to_next_page(last_match_date=last_game_date, match_date=match_date))


if __name__ == '__main__':
    unittest.main()
