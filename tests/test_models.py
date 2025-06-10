import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flashcards.app import create_app
from flashcards.models import db, FlashCard, Lesson, lesson_cards

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app.config['TESTING'] = True
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_card_lesson_relation(self):
        card = FlashCard(front_text='front', back_text='back')
        db.session.add(card)
        lesson = Lesson(title='Lesson1')
        db.session.add(lesson)
        db.session.commit()
        db.session.execute(lesson_cards.insert().values(lesson_id=lesson.id, card_id=card.id, order_index=0))
        db.session.commit()
        self.assertEqual(lesson.cards[0].id, card.id)
        self.assertEqual(card.lessons.first().id, lesson.id)

if __name__ == '__main__':
    unittest.main()

