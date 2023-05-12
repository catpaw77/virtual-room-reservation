from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, email_validator
from wtforms import ValidationError, HiddenField
from myproject.models import User
import datetime
from wtforms.fields.html5 import DateField
from wtforms.fields.html5 import TimeField


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
                             DataRequired(), EqualTo('pass_confirm', message='密碼需要吻合')])
    pass_confirm = PasswordField(
        'Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


def check_email(self, field):
    """檢查Email"""
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('電子郵件已經被註冊過了')


def check_username(self, field):
    """檢查username"""
    if User.query.filter_by(username=field.data).first():
        raise ValidationError('使用者名稱已經存在')


class BookRoomForm(FlaskForm):
    room_choices = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    hour_choices = [('09:00', '09:00'), ('10:00', '10:00'), ('11:00', '11:00'), ('12:00', '12:00'), ('13:00', '13:00'),     #('9:00', '9:00') 換成 ('09:00', '09:00') 讓每個字串長度相同，方便比大小 2021/12/03
                    ('14:00', '14:00'), ('15:00', '15:00'), ('16:00', '16:00'), ('17:00', '17:00'), ('18:00', '18:00')]
    date = DateField('Date', format='%Y-%m-%d',
                     validators=[DataRequired()], default=datetime.date.today())  # 預設日期為當天

    start_time = SelectField(
        'Start Time', choices=hour_choices, validate_choice=[DataRequired()])
    end_time = SelectField('End Time', choices=hour_choices,
                           validators=[DataRequired()])

    room = SelectField('Room', choices=room_choices,
                       validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    attendee = StringField('Attendees', validators=[
                           DataRequired()])  # 輸入為字串，以英式逗號分隔
    meeting_name = StringField('Meeting Name', validators=[DataRequired()])
    id = HiddenField(0)
    submit = SubmitField('Book Room')

class HomePageForm(FlaskForm):
    
    date = DateField('Date', format='%Y-%m-%d',
                     validators=[DataRequired()], default=datetime.date.today())  # 預設日期為當天

   
    id = HiddenField(0)
    submit = SubmitField('Search')
