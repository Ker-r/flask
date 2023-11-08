from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    ''' Форма авторизации '''
    # validators ссылается на список валидаторов для проверки корректности
    #  введеных данных в поле Email
    email = StringField('Email: ', validators=[Email('Некорректный email')])
    # DataRequired требует, чтобы в этом поле ввода был хотя бы 1 символ,
    # Length требует, чтобы в этом поле ввода было от 4 до 100 символов
    paw = PasswordField('Пароль: ', validators=[DataRequired(), Length(
        min=4, max=100, message='Пароль должен быть от 4 до 100 символов')])
    remember = BooleanField('Запомнить', default=False)
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(
        min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(
                                                    min=4, max=100,
                                                    message="Пароль должен быть от 4 до 100 символов")])

    # EqualTo совпадают ли поля psw с psw2
    psw2 = PasswordField("Повтор пароля: ",
                         validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")
