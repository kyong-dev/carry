from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FloatField, HiddenField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Regexp, Length, Email, EqualTo, ValidationError
from carry.models import User


class RegistrationForm(FlaskForm):
    """A flexible form validation for Registration

    :param formdata: Used to pass data coming from the enduser, usually request.POST or equivalent. formdata should be some sort of request-data wrapper which can get multiple parameters from the form input, and values are unicode strings

    """
    username = StringField('Username', validators=[DataRequired(), Regexp(
        '^\w+$', message="Username must contain only letters numbers or underscore")])
    password = PasswordField('Password', validators=[DataRequired(), Length(
        min=8, message="Password should be more than 8 characters")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), Regexp(
        '^\w+$', message="Firstname must contain only letters numbers or underscore")])
    lastname = StringField('Last Name', validators=[DataRequired(), Regexp(
        '^\w+$', message="Lastname must contain only letters numbers or underscore")])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """A function for checking if username already exists in the database

        :param username: Username
        :type username: string, essential
        :return: ValidationError()
        :rtype: function

        """ 
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """A function for checking if email already exists in the database

        :param email: Email
        :type email: string, essential
        :return: ValidationError()
        :rtype: function
        
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    """A flexible form validation for Login

    :param formdata: Used to pass data coming from the enduser, usually request.POST or equivalent. formdata should be some sort of request-data wrapper which can get multiple parameters from the form input, and values are unicode strings

    """
    username = StringField('Email / Username', validators=[DataRequired(), Regexp(
        '^\w|[\w.\-_]+\@[\w.\-_]+\.\w+$', message="Username must contain only letters numbers or underscore")])
    password = PasswordField('Password', validators=[DataRequired(), Length(
        min=8, message="Password should be more than 8 characters")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    """A flexible form validation for Profile Update

    :param formdata: Used to pass data coming from the enduser, usually request.POST or equivalent. formdata should be some sort of request-data wrapper which can get multiple parameters from the form input, and values are unicode strings

    """
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), Regexp(
        '^\w+$', message="Username must contain only letters numbers or underscore")])
    lastname = StringField('Last Name', validators=[DataRequired(), Regexp(
        '^\w+$', message="Username must contain only letters numbers or underscore")])
    location = SelectField('Location', choices=[(
        'melbourne', 'Melbourne')], validators=[DataRequired()])
    profile_url = FileField('Update Profile Picture', validators=[
                            FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Update')


class BookingForm(FlaskForm):
    """A flexible form validation for Booking Detail

    :param formdata: Used to pass data coming from the enduser, usually request.POST or equivalent. formdata should be some sort of request-data wrapper which can get multiple parameters from the form input, and values are unicode strings

    """
    user_id = HiddenField('User ID', validators=[DataRequired()])
    car_id = HiddenField('Car ID', validators=[DataRequired()])
    duration = HiddenField('Duration', validators=[DataRequired()])
    start_datetime = HiddenField('Start Date', validators=[DataRequired()])
    end_datetime = HiddenField('End Date', validators=[DataRequired()])
    submit = SubmitField('Book')


class NewBookingForm(FlaskForm):
    """A flexible form validation for New Booking

    :param formdata: Used to pass data coming from the enduser, usually request.POST or equivalent. formdata should be some sort of request-data wrapper which can get multiple parameters from the form input, and values are unicode strings

    """
    car_id = HiddenField('Car ID', validators=[DataRequired()])
    start_datetime = HiddenField('Start Date', validators=[DataRequired()])
    end_datetime = HiddenField('End Date', validators=[DataRequired()])
    duration = HiddenField('Duration', validators=[DataRequired()])
    submit = SubmitField('Confirm', validators=[DataRequired()])
