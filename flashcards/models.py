from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

lesson_cards = db.Table(
    'lesson_cards',
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), primary_key=True),
    db.Column('card_id', db.Integer, db.ForeignKey('flash_card.id'), primary_key=True),
    db.Column('order_index', db.Integer, default=0),
    db.Column('last_score', db.Integer)
)

class FlashCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    front_text = db.Column(db.Text, nullable=False)
    back_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cards = db.relationship('FlashCard', secondary=lesson_cards,
                            backref=db.backref('lessons', lazy='dynamic'),
                            order_by=lesson_cards.c.order_index)
