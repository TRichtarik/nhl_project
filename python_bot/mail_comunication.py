# this part will basically cover email comunication
# either sending email with needed statistics or recieving emails for processing
import base64
from email.message import EmailMessage
import email
import smtplib
import imaplib
import ssl

USERNAME = "nhl.statistiky@gmail.com"
PASSWORD = "hdohjcyfcgltxcud"


def send_stats(subject: str, filename_http: str, reciever: str) -> None:
    # ["richtom21@gmail.com", "martina.paliarikova@gmail.com"]
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"

    msg = EmailMessage()
    msg['Subject'] = f'{subject}'
    msg['From'] = USERNAME
    msg['To'] = reciever

    with open(filename_http, 'r') as fp:
        message = fp.read().encode('ascii', 'ignore').decode('ascii')
        msg.set_content(message, subtype='html')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)


def sender_decode(sender):
    parsed_string = sender.split("?")

    decoded = base64.b64decode(parsed_string[3]).decode(parsed_string[1], "ignore")
    return decoded


def read_email():
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(USERNAME, PASSWORD)
    imap.select('INBOX')

    status, response = imap.uid('search', None, 'UNSEEN')
    if status == 'OK':
        unread_msg_nums = response[0].split()
    else:
        unread_msg_nums = []
    data_list = []
    for e_id in unread_msg_nums:
        data_dict = {}
        e_id = e_id.decode('utf-8')
        _, response = imap.fetch(str(e_id), '(RFC822)')

        _, response = response[0]

        html = response.decode('ascii')
        email_message = email.message_from_string(html)
        # data_dict['mail_to'] = email_message['To']
        if '?' in email_message['Subject']:
            data_dict['Subject'] = sender_decode(email_message['Subject'])
        else:
            data_dict['Subject'] = email_message['Subject']
        _, data_dict['From'] = email.utils.parseaddr(email_message['From'])
        # data_dict['body'] = email_message.get_payload()
        data_list.append(data_dict)

    # Mark them as seen
    print(data_list)
    for e_id in unread_msg_nums:
        imap.store(e_id, '+FLAGS', '\Seen')

    return data_list
