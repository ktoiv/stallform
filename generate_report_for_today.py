import smtplib, ssl
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from jinja2 import Environment, FileSystemLoader
from datetime import date

from app.analyzer.start_list_analyzer import get_todays_horses
from app.service.data_update_service import init_db_connection, update_database



init_db_connection()
update_database()


cards = get_todays_horses()

env = Environment( loader = FileSystemLoader('templates') )
template = env.get_template('report_template_FI.html')


content = template.render(cards=cards)

sender_email = "stallform@gmail.com"
receiver_emails = os.environ['RECEIVER_MAIL'].split(';')
password = os.environ['MAIL_PASSWORD']


message = MIMEMultipart("alternative")
message["Subject"] = 'Raviraportti {}.{}.{}'.format(date.today().day, date.today().month, date.today().year)
message["From"] = sender_email

part = MIMEText(content, 'html')

message.attach(part)

port = 465
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login(sender_email, password)
    for receiver_email in receiver_emails:
        message["To"] = receiver_email
        print('sending email to', receiver_email)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )