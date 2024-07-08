from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import threading
from playwright_script import run_playwright_script
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ce5713050fc8ff49a4ebf3528b6a14e9'

class SubitemForm(FlaskForm):
    board_id = StringField('Board ID', validators=[DataRequired()])
    submit = SubmitField('Run Script')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SubitemForm()
    if form.validate_on_submit():
        board_id = form.board_id.data
        api_key = os.getenv('MONDAY_API_KEY')
        # Start the Playwright script in a new thread to avoid blocking the Flask app
        threading.Thread(target=run_playwright_script, args=(api_key, board_id)).start()
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
