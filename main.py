import time
import pre_game_stats
import game_day_stats
from datetime import datetime
from typing import List
import smtplib
import ssl


#  #########################
#  ## NHLstatsFORlearning ##
#  #########################

def send_stats(filename: str):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"

    sender_email = "nhl.statistiky@gmail.com"  # Enter your address
    password = "hdohjcyfcgltxcud"

    receiver_email_mine = "richtom21@gmail.com"  # Enter receiver address
    receiver_email_love = "martina.paliarikova@gmail.com"

    message = f"Subject: {filename}\n"
    with open(filename, 'r') as fp:
        message += fp.read()

    message = message.encode('ascii', 'ignore').decode('ascii')
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email_mine, message)
        # server.sendmail(sender_email, receiver_email_love, message)


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


        for file_name in files:
            print(f"Sending email: {file_name}")
            send_stats(file_name)

        print("Sleeping...")
        time.sleep(60)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
