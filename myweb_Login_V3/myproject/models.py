from myproject import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#引入SMTP Library 來實踐自動寄信功能
from email.mime.text import MIMEText
import smtplib

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    # columns
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, email, username, password):
        """初始化"""
        self.email = email
        self.username = username
        # 實際存入的為password_hash，而非password本身
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """檢查使用者密碼"""
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Meeting(db.Model):
    __tablename__ = 'meetings'

    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(64))
    date = db.Column(db.String(64))
    start_time = db.Column(db.String(64))
    end_time = db.Column(db.String(64))
    room = db.Column(db.String(64))     #db.Column(db.Integer) 改為 db.Column(db.String(64)) 2021/12/03
    description = db.Column(db.String(256))
    attendees = db.Column(db.String(64))
    meeting_name = db.Column(db.String(64))

    def __init__(self, host, date, start_time, end_time, room, description, attendees, meeting_name):
        self.host = host
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.room = room
        self.description = description
        self.attendees = attendees
        self.meeting_name = meeting_name

#自動寄信
def sendmailSMTP(subject, messageContent, attendees):
    # Account infomation load
    #account = json.load(open('Account.json', 'r', encoding='utf-8'))
    gmailUser = 'swroomie15@gmail.com'#account['Account']''
    gmailPasswd = '@SWRoomie1500'#account['password']
    receivers = attendees.split(',')#['benjaminyolo1214@gmail.com', 'wtoyo958@gmail.com', 'b10830226@gapps.ntust.edu.tw']
    # Create message
    emails = [t.split(',') for t in receivers]
    message = MIMEText(messageContent, 'plain', 'utf-8')#MIMEText('Give me a Test!', 'plain', 'utf-8')
    message['Subject'] = subject#'Single Test'
    message['From'] = gmailUser
    message['To'] = ','.join(receivers)

    # Set smtp
    smtp = smtplib.SMTP("smtp.gmail.com:587")
    smtp.ehlo()
    smtp.starttls()
    smtp.login(gmailUser, gmailPasswd)

    # Send msil
    smtp.sendmail(message['From'], receivers, message.as_string())
    print('Send mails OK!')
