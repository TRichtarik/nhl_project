import requests, csv, os
from typing import List
from filecmp import cmp
from datetime import datetime, timedelta

"""
This stats could by in format like this
fullname; goals; assists; points; +/-a
"""


def get_finished_games_id(game_day: str) -> List[str]:
    schedule_url_today = f"https://statsapi.web.nhl.com/api/v1/schedule?date={game_day}"

    response = requests.get(schedule_url_today)
    if response.status_code != 200:
        print(f"Error: {response.reason}")
        return []

    finished_games = []

    for date in response.json()["dates"]:
        for game in date["games"]:
            # Finished codes = {5,6,7}
            if game["status"]["statusCode"] in {"5", "6", "7"}:
                finished_games.append(game["gamePk"])
            else:
                return []

    return finished_games


def create_game_day_stats(filename: str) -> bool:
    """

    :param filename:
    :return: True if all games of today are finished
             False otherwise or not changes were made
    """
    game_day = datetime.today() - timedelta(days=1, hours=00, minutes=00)
    game_day = game_day.strftime("%Y-%m-%d")

    finished_games = get_finished_games_id(game_day)
    if not finished_games:
        return False

    fieldnames = ['full_name', 'goals', 'assists', '+/-']
    rows = []

    for game_id in finished_games:
        url = f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/boxscore"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: {response.reason}")
        process_game(response, rows)

    with open("new", 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if not cmp("new", filename):
        os.remove(filename)
        os.renames("new", filename)
        return True

    os.remove("new")
    return False


def process_game(response, rows) -> None:
    for where in ["home", "away"]:
        for player in response.json()["teams"][where]["players"]:
            if (response.json()["teams"][where]["players"][player]["person"]["birthCountry"] == "SVK" and
                    response.json()["teams"][where]["players"][player]["position"]["name"] != "Goalie"):
                print(response.json()["teams"][where]["players"][player]["person"]["fullName"])
                if response.json()["teams"][where]["players"][player]["stats"] == {}:
                    break
                # print(response.text)
                goals = response.json()["teams"][where]["players"][player]["stats"]["skaterStats"]["goals"]
                new_player = {"full_name": response.json()["teams"][where]["players"][player]["person"]["fullName"],
                              "goals": goals,
                              "assists": response.json()["teams"][where]["players"][player]["stats"]["skaterStats"][
                                  "assists"],
                              "+/-": response.json()["teams"][where]["players"][player]["stats"]["skaterStats"][
                                  "plusMinus"]}
                rows.append(new_player)
