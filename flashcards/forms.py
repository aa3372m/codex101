from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired

class CardForm(FlaskForm):
    front_text = TextAreaField('Front', validators=[DataRequired()])
    back_text = TextAreaField('Back', validators=[DataRequired()])
    submit = SubmitField('Save')

class LessonForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    cards = SelectMultipleField('Cards', coerce=int)
    order = HiddenField('Order')
    submit = SubmitField('Save')

class ScoreForm(FlaskForm):
    card_id = HiddenField('Card ID', validators=[DataRequired()])
    score = HiddenField('Score', validators=[DataRequired()])
