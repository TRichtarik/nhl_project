import mail_comunication
import pandas
import time
import os
import stats


#  #########################
#  ## NHLstatsFORlearning ##
#  ## NHLstatsFORlearning1<#
#  #########################


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
    popis
    :param dir_path: Directory where statistics are stored.
    :param file_name: Specific statistic name.
    :return: Path to specific file. If file does not exist, we create one.
    """

    file_path = os.path.join(dir_path, file_name)

    if not os.path.exists(file_path):
        open(file_path, 'w').close()

    return file_path


def create_html_table(file_name: str):
    csv_file = pandas.read_csv(file_name)
    html_file = f"{file_name}_html"
    csv_file.to_html(html_file)
    return html_file



def process_request():
    # name of stat: (path to stat_file, is updated, function to update stat)

    # help
    # {day=format} / {month=format} - {player=list them} / {player=nationality list} / {team=list them}
    #                                                       - {all_s, all_m, all_l /goals-points-plusminus}
    # -date/game day format
    # -date/today players format
    # -month player/players stats
    # -month team stats
    # "Today's players.csv": ("", False, stats.update_stats)

    options = {'help': stats.print_help,
               'game day': stats.game_day}
    file_name = 'temp'

    while True:
        mails = mail_comunication.read_email()

        for mail in mails:
            if mail['Subject'] not in options.keys():
                function = options['help']
            else:
                function = options[mail['Subject']]

            function(file_name)

            file_name = create_html_table(file_name)

            print(f"Sending email : {mail['Subject']} to {mail['From']}")

            mail_comunication.send_stats(mail['Subject'], file_name, mail['From'])
            os.remove(file_name)


        print('Sleeping...')
        time.sleep(10)


def main() -> None:
    process_request()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
