import requests
import csv, os
from filecmp import cmp
from typing import List, Optional
from datetime import datetime, timedelta


def get_today_game_id(game_day: str) -> List[int]:
    today_schedule_url = f"https://statsapi.web.nhl.com/api/v1/schedule?date={game_day}"

    response = requests.get(today_schedule_url)
    if response.status_code != 200:
        print(f"Error: {response.reason}")
        return []

    game_ids = []

    for date in response.json()["dates"]:
        for game in date["games"]:
            game_ids.append(game["gamePk"])

    return game_ids


def print_stats_overall(filename: str) -> bool:
    """

    :param filename:
    :return: True if there are games scheduled and changes in roasters were made
             False otherwise
    """

    game_day = datetime.today() - timedelta(days=00, hours=00, minutes=00)
    game_day = game_day.strftime("%Y-%m-%d")

    game_ids = get_today_game_id(game_day)
    if not game_ids:
        return False

    fieldnames = ['team_name', 'player_name']
    rows = []

    for game_id in game_ids:
        url = f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/boxscore"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: {response.reason}")
        load_roaster(response, rows)

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


def load_roaster(response, rows) -> None:
    for where in ["home", "away"]:
        for player in response.json()["teams"][where]["players"]:
            if response.json()["teams"][where]["players"][player]["person"]["birthCountry"] == "SVK":
                full_name = response.json()["teams"][where]["players"][player]["person"]["fullName"]
                team_name = response.json()["teams"][where]["team"]["name"]
                new_game = {"team_name": team_name,
                            "player_name": full_name}
                rows.append(new_game)
