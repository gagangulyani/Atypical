from wtforms.validators import InputRequired, Email, Length, ValidationError
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                     RadioField, IntegerField, TextAreaField, SelectField)
from flask_wtf.file import FileField, FileRequired, FileAllowed
from models.categories import Category
from models.database import Database
from string import punctuation


def checkForJunk(form = None, field = None, usrtext= None):
    punct = punctuation.replace('_', '')
    if not field:
        field = {'data': usrtext}
    for i in field.data:
        if i in punct:
            if usrtext:
                return True
            else:
                raise ValidationError(
                'Only Alphabets, Numbers and Underscores Allowed!')


def StrongPassword(form, field):
    punct = punctuation
    numbers = "0123456789"
    alphabets = "QWERTYUIOPASDFGHJKLZXCVBNM"

    errors = {
        "isSpecial": 'Special Symbol',
        "isNumber": 'Number',
        'isUpper': 'UpperCase Character'
    }

    if any(char in field.data for char in punct):
        errors.pop('isSpecial')

    if any(char in field.data for char in numbers):
        errors.pop('isNumber')

    if any(char in field.data for char in alphabets):
        errors.pop('isUpper')

    if errors:
        message = "Password Must Contain atleast 1 "
        errors = [errors[msg] for msg in errors]
        extra = ", ".join(errors[:-1]) 
        if extra:
            extra2 = " and " + errors[-1]
        else:
            extra2 = errors[-1]
        
        message += extra + extra2

        raise ValidationError(message)

class SignupForm(FlaskForm):

    name = StringField("Name",
                       validators=[
                           InputRequired('Please Enter your Name'),
                           checkForJunk
                       ], render_kw={"placeholder": "Martha Jones"})

    email = StringField("Email",
                        validators=[
                            InputRequired('Please Enter your Email'),
                            Email('Please Enter a valid email address')
                        ], render_kw={
                            "placeholder": "marthajones@example.com"})

    password = PasswordField("Password",
                             validators=[
                                 InputRequired('Please Enter your Password'),
                                 Length(min=6, max=16,
                                        message='Password Must be 8-16\
 Characters Long'), StrongPassword],
                             render_kw={"placeholder": "******"})

    gender = RadioField("Gender",
                        choices=[
                            ('M', 'Male'),
                            ('F', 'Female'),
                            ('O', 'Other')],
                        validators=[
                            InputRequired('Please Select a Gender')
                        ])

    age = IntegerField('Age', validators=[
                       InputRequired('Please Enter a Valid Age')],
                       render_kw={
        "placeholder": "23"})

    submit = SubmitField("Signup",
                         validators=[
                             InputRequired()
                         ])


class LoginForm(FlaskForm):
    username = StringField("Email/Username",
                           validators=[
                               InputRequired(
                                   'Please Enter your Username Or Email'),
                               Length(min=4, max=50,
                                      message='Invalid Username')],
                           render_kw={"placeholder": "Martha_Jones96"})

    password = PasswordField("Password",
                             validators=[
                                 InputRequired('Please Enter your Password'),
                                 Length(min=6, max=16,
                                        message='Invalid Password')],
                             render_kw={"placeholder": "******"})

    submit = SubmitField("Login",
                         validators=[
                             InputRequired()
                         ])


Database.initialize('Atypical')
categories = Category.getAllCategories(True)
categories = [(cat, cat) for cat in categories]
# print(categories)


class UploadForm(FlaskForm):
    photo = FileField('Upload your Picture', validators=[
        FileRequired('File not selected!'),
        FileAllowed(['jpg', 'png','jpeg'], 'Images only!')
    ])

    # category = SelectField("Category",
    #                        choices=categories,
    #                        validators=[
    #                            InputRequired('Please Choose a Category')])

    description = TextAreaField('Description')

    submit = SubmitField("Upload",
                         validators=[
                             InputRequired()
                         ])
