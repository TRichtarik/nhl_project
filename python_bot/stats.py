import requests
import csv
import os
from filecmp import cmp
from typing import List, Set
from datetime import datetime, timedelta

STATISTICS_HEADER = {"Game day statistics.csv": ['full_name', 'goals', 'assists', 'plus_minus'],
                     "Today's players.csv": ['team_name', 'full_name']}

Response = requests.models.Response


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

        if file_name == "Game day statistics.csv":
            return self.today_ended
        return self.today_in_progress

    def get_time(self) -> str:
        day = 1

        if not self.today_in_progress:
            day = 0

        game_day = datetime.today() - timedelta(days=day, hours=00, minutes=00)
        game_day = game_day.strftime("%Y-%m-%d")
        return game_day


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
            elif game["status"]["statusCode"] not in {"1", "8", "9"}:
                games.today_in_progress.add(game["gamePk"])


def update_stats(games: Games, file_name: str, file_path: str, temp_file: str) -> bool:
    if not games.get_game_ids(file_name):
        return False

    players: List[Player] = []
    for game_id in games.get_game_ids(file_name):
        url = f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/boxscore"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: {response.reason}")
            return False

        load_roaster(response, players)

    if not players:
        return False

    return write_statistics_to_file(file_name, file_path, temp_file, players)


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


def write_statistics_to_file(file_name: str, file_path: str, temp_file: str, players: List[Player]) -> bool:
    rows = []

    for player in players:
        rows.append(dict((attribute, getattr(player, f"{attribute}")) for attribute in STATISTICS_HEADER[file_name]))

    with open(temp_file, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=STATISTICS_HEADER[file_name])
        writer.writeheader()
        writer.writerows(rows)

    if not cmp(temp_file, file_path):
        os.remove(file_path)
        os.renames(temp_file, file_path)
        return True

    os.remove(temp_file)
    return False
