import os
from flask import Flask, render_template, redirect, url_for, flash, request
from .config import Config
from .models import db, FlashCard, Lesson, lesson_cards
from .forms import CardForm, LessonForm, ScoreForm


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return redirect(url_for('lesson_list'))

    @app.route('/cards')
    def card_list():
        cards = FlashCard.query.all()
        return render_template('card_list.html', cards=cards)

    @app.route('/cards/new', methods=['GET', 'POST'])
    def card_new():
        form = CardForm()
        if form.validate_on_submit():
            card = FlashCard(front_text=form.front_text.data, back_text=form.back_text.data)
            db.session.add(card)
            db.session.commit()
            return redirect(url_for('card_list'))
        if form.errors:
            flash('Error creating card')
        return render_template('card_form.html', form=form)

    @app.route('/cards/<int:id>/edit', methods=['GET', 'POST'])
    def card_edit(id):
        card = FlashCard.query.get_or_404(id)
        form = CardForm(obj=card)
        if form.validate_on_submit():
            card.front_text = form.front_text.data
            card.back_text = form.back_text.data
            db.session.commit()
            return redirect(url_for('card_list'))
        if form.errors:
            flash('Error updating card')
        return render_template('card_form.html', form=form)

    @app.route('/lessons')
    def lesson_list():
        lessons = Lesson.query.order_by(Lesson.created_at.desc()).all()
        return render_template('lesson_list.html', lessons=lessons)

    @app.route('/lessons/new', methods=['GET', 'POST'])
    def lesson_new():
        form = LessonForm()
        cards = FlashCard.query.all()
        form.cards.choices = [(c.id, c.front_text) for c in cards]
        selected = [c.id for c in cards]
        if form.validate_on_submit():
            lesson = Lesson(title=form.title.data)
            db.session.add(lesson)
            db.session.flush()
            order_ids = [int(i) for i in form.order.data.split(',') if i]
            selected_ids = [int(cid) for cid in request.form.getlist('cards')]
            order_map = {cid: idx for idx, cid in enumerate(order_ids)}
            for cid in selected_ids:
                db.session.execute(lesson_cards.insert().values(
                    lesson_id=lesson.id, card_id=cid,
                    order_index=order_map.get(cid, 0), last_score=None))
            db.session.commit()
            return redirect(url_for('lesson_list'))
        return render_template('lesson_form.html', form=form, cards=cards, selected=selected)

    def get_lesson_cards(lesson):
        stmt = db.select(FlashCard, lesson_cards.c.last_score).join(lesson_cards).where(
            lesson_cards.c.lesson_id == lesson.id).order_by(lesson_cards.c.order_index)
        return db.session.execute(stmt).all()

    @app.route('/lessons/<int:id>/run', methods=['GET', 'POST'])
    def run_lesson(id):
        lesson = Lesson.query.get_or_404(id)
        cards_with_scores = get_lesson_cards(lesson)
        index = int(request.args.get('i', 0))
        if index >= len(cards_with_scores):
            return redirect(url_for('lesson_summary', id=lesson.id))
        card, score = cards_with_scores[index]
        form = ScoreForm()
        if form.validate_on_submit():
            db.session.execute(lesson_cards.update().where(
                (lesson_cards.c.lesson_id == lesson.id) & (lesson_cards.c.card_id == int(form.card_id.data)))
                .values(last_score=int(form.score.data)))
            db.session.commit()
            return redirect(url_for('run_lesson', id=lesson.id, i=index + 1))
        return render_template('run_lesson.html', lesson=lesson, card=card, form=form)

    @app.route('/lessons/<int:id>/summary')
    def lesson_summary(id):
        lesson = Lesson.query.get_or_404(id)
        results = get_lesson_cards(lesson)
        return render_template('lesson_summary.html', lesson=lesson, results=results)

    @app.route('/lessons/<int:id>/summary', methods=['POST'])
    def create_next_lesson(id):
        lesson = Lesson.query.get_or_404(id)
        cards = [card for card, score in get_lesson_cards(lesson) if score is not None and score <= 3]
        if not cards:
            flash('No cards scored 3 or below')
            return redirect(url_for('lesson_summary', id=id))
        new_lesson = Lesson(title=f"Follow-up to {lesson.title}")
        db.session.add(new_lesson)
        db.session.flush()
        for idx, card in enumerate(cards):
            db.session.execute(lesson_cards.insert().values(
                lesson_id=new_lesson.id, card_id=card.id, order_index=idx, last_score=None))
        db.session.commit()
        return redirect(url_for('run_lesson', id=new_lesson.id))

    return app

if __name__ == '__main__':
    debug = os.environ.get('FLASK_ENV') == 'development'
    app = create_app()
    app.run(debug=debug)

