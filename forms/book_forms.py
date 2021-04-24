from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class AddBookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class SearchBookForm(FlaskForm):
    text = StringField('Поиск:', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')