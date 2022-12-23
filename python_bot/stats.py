import requests
import csv
import os
from typing import List, Set
from datetime import datetime, timedelta

import mail_comunication

STATISTICS_HEADER = {"game day": ['full_name', 'goals', 'assists', 'plus_minus'],
                     "Today's players.csv": ['team_name', 'full_name']}

Response = requests.models.Response.json


class Player:
    def __init__(self) -> None:
        self.full_name = None
        self.team_name = None
        self.goals = 0
        self.assists = 0
        self.plus_minus = 0

    def parse_player_json(self, response: Response, where: str, player: str) -> None:
        self.full_name = response["teams"][where]["players"][player]["person"]["fullName"]
        self.team_name = response["teams"][where]["team"]["name"]
        if response["teams"][where]["players"][player]["stats"] == {}:
            return
        if response["teams"][where]["players"][player]["position"]["name"] == "Goalie":
            return
        self.goals = response["teams"][where]["players"][player]["stats"]["skaterStats"]["goals"]
        self.assists = response["teams"][where]["players"][player]["stats"]["skaterStats"]["assists"]
        self.plus_minus = response["teams"][where]["players"][player]["stats"]["skaterStats"]["plusMinus"]


class Games:
    def __init__(self) -> None:
        self.today_games_counter = 0
        self.today_in_progress: Set[str] = set()
        self.today_ended: Set[str] = set()

    def get_game_ids(self, file_name: str) -> Set[str]:
        if file_name == "game day":
            return self.today_ended
        return self.today_in_progress

    def get_time(self) -> str:
        os.environ['TZ'] = 'US/Eastern'

        game_day = datetime.today() - timedelta(days=1, hours=00, minutes=00)
        game_day = game_day.strftime("%Y-%m-%d")
        return game_day


def print_help(file_name: str):
    helper = """--- Welcome to nhl via mail stats ---\n
    --- TYPE --- FUNCTIONALITY --- \n
    Currently implemented stats:\n
    ------------------------------------\n
    Will be implemented soon:\n
    -------------------------------------\n
    How to use:\n
    Simply by just typing stats type in SUBJECT of email'\n
    send to address nhl.statistiky@gmail.com') \n
    Recognition of stat type is case and syntax sensitive!\n
    -------------------------------------\n"""

    with open(file_name, 'w') as temp_file:
        temp_file.write(helper)


def game_day(file_name: str):
    games = Games()
    fill_game_ids(games)
    update_stats(games, file_name, 'game day')


def fill_game_ids(games: Games) -> None:
    schedule_url_today = f"https://statsapi.web.nhl.com/api/v1/schedule?date={games.get_time()}"

    response = requests.get(schedule_url_today)
    if response.status_code != 200:
        print(f"Error: {response.reason}")
        return None

    games.today_games_counter = response.json()['totalGames']

    for date in response.json()["dates"]:
        for game in date["games"]:
            # Finished codes = {5,6,7}
            if game["status"]["statusCode"] in {"5", "6", "7"}:
                games.today_ended.add(game["gamePk"])
            else:
                games.today_in_progress.add(game["gamePk"])


def update_stats(games: Games, temp_file: str, stat_type: str) -> bool:
    players: List[Player] = []
    for game_id in games.get_game_ids(stat_type):
        url = f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/boxscore"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: {response.reason}")
            return False

        load_roaster(response, players)

    if not players:
        return False

    return write_statistics_to_file(stat_type, temp_file, players)


def load_roaster(response: Response, players: List[Player]) -> bool:
    for where in ["home", "away"]:
        if response.json()["teams"][where]["players"] == {}:
            return False
        for player in response.json()["teams"][where]["players"]:
            if response.json()["teams"][where]["players"][player]["person"]["birthCountry"] == "SVK":
                new_player = Player()
                new_player.parse_player_json(response.json(), where, player)
                players.append(new_player)
    return True


def write_statistics_to_file(stat_type, temp_file: str, players: List[Player]) -> bool:
    rows = []

    for player in players:
        rows.append(dict((attribute, getattr(player, f"{attribute}")) for attribute in STATISTICS_HEADER[stat_type]))

    with open(temp_file, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=STATISTICS_HEADER[stat_type])
        writer.writeheader()
        writer.writerows(rows)

    return True
