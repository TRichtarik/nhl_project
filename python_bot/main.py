import smtplib
import ssl
import pandas
import time
import os
import stats
from email.message import EmailMessage


#  #########################
#  ## NHLstatsFORlearning ##
#  ## NHLstatsFORlearning1<#
#  #########################

def send_stats(subject: str, filename_http: str) -> None:
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"

    msg = EmailMessage()
    msg['Subject'] = f'{subject}'
    msg['From'] = "nhl.statistiky@gmail.com"
    msg['To'] = "richtom21@gmail.com"
    password = "hdohjcyfcgltxcud"

    with open(filename_http, 'r') as fp:
        message = fp.read().encode('ascii', 'ignore').decode('ascii')
        msg.set_content(message, subtype='html')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(msg['From'], password)
        server.send_message(msg)


def get_stats_dir_path(dir_name: str) -> str:
    """
    Creates directory to store all statistics in csv form if non-existent
    :param dir_name: name of the directory
    :return: Path to directory containing statistics
    """

    parent_dir = os.path.dirname(os.getcwd())
    path = os.path.join(parent_dir, dir_name)

    if not os.path.exists(path):
        os.mkdir(path)

    return path


def get_stats_file_path(dir_path: str, file_name: str) -> str:
    """
    :param dir_path: Directory where statistics are stored.
    :param file_name: Specific statistic name.
    :return: Path to specific file. If file does not exist, we create one.
    """

    file_path = os.path.join(dir_path, file_name)

    if not os.path.exists(file_path):
        open(file_path, 'w').close()

    return file_path


def main() -> None:
    """
    Loads all different statistics into text file named after statistic.
    Notifies user via email if changes in statistic happens.
    :return:
    """

    # name of stat: (path to stat_file, is updated, function to update stat)
    statistics = {"Game day statistics.csv": ("", False, stats.update_stats),
                  "Today's players.csv": ("", False, stats.update_stats)}

    dir_name = "csv_statistics"
    dir_path = get_stats_dir_path(dir_name)
    temp_file_path = get_stats_file_path(dir_path, "temp_file")
    games = stats.Games()

    while True:

        stats.fill_game_ids(games)

        for file_name, (_, is_updated, function) in statistics.items():
            print(f"Loading {file_name}")
            file_path = get_stats_file_path(dir_path, file_name)
            is_updated = function(games, file_name, file_path, temp_file_path)
            statistics[file_name] = (file_path, is_updated, function)

        for file_name, (file_path, is_updated, function) in statistics.items():
            if not is_updated:
                continue

            csv_file = pandas.read_csv(file_path)
            html_file = f"{file_name}_html"
            csv_file.to_html(html_file)
            print(f"Sending email: {file_name}")
            send_stats(f"{file_name}", html_file)
            os.remove(html_file)
            statistics[file_name] = (file_path, False, function)

        if games.today_ended == games.today_games_counter:
            games = stats.Games()

        print("Sleeping...")
        time.sleep(10 * 60)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
