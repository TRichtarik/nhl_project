import smtplib
import ssl
import pandas
import time
import os
from datetime import datetime
from email.message import EmailMessage

import game_day_stats
import pre_game_stats


#  #########################
#  ## NHLstatsFORlearning ##
#  ## NHLstatsFORlearning1<#
#  #########################

def send_stats(subject: str, filename: str):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"

    msg = EmailMessage()
    msg['Subject'] = f'{subject}'
    msg['From'] = "nhl.statistiky@gmail.com"
    msg['To'] = "richtom21@gmail.com"

    password = "hdohjcyfcgltxcud"

    with open(filename, 'r') as fp:
        msg.set_content(fp.read().encode('ascii', 'ignore').decode('ascii'), subtype='html')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(msg['From'], password)
        server.send_message(msg)


def main() -> None:
    # this part focuses on slovak players in a current day games
    game_day = datetime.today()
    game_day = game_day.strftime("%Y-%m-%d")
    while True:
        files = {"Game day statistics", "Today's players"}
        print("Loading Today's players.")
        new_pre_game_stats = pre_game_stats.print_stats_overall("Today's players")
        print("Loading Game day statistics.")
        day_is_finished = game_day_stats.create_game_day_stats("Game day statistics")
        if not day_is_finished:
            files.remove("Game day statistics")

        if not new_pre_game_stats:
            files.remove("Today's players")

        for file_name in files:
            csv_file = pandas.read_csv(file_name)
            html_file = f"{file_name}_html"
            csv_file.to_html(html_file)
            print(f"Sending email: {file_name}")
            send_stats(f"{file_name}", html_file)
            os.remove(html_file)

        print("Sleeping...")
        time.sleep(10 * 60)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
