import multiprocessing
import multiprocessing.process
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '074c12072674c95c390ee09218f355ce1d54966a589d6e90'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'

db = SQLAlchemy(app)

class MessageForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    phone_number = StringField('Phone Number', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    content = TextAreaField('Content', validators=[InputRequired(), Length(min=10)])

class MessageModel(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_message_sync/', methods=['GET', 'POST'])
def add_message_sync():
    form = MessageForm()
    if form.validate_on_submit():
        new_message = MessageModel(name=form.name.data,
                                    last_name=form.last_name.data,
                                    phone_number=form.phone_number.data,
                                    email=form.email.data,
                                    content=form.content.data)
        db.session.add(new_message)
        db.session.commit()
        flash('Message added successfully!')
        return redirect(url_for('index'))
    return render_template('add_message_sync.html', form=form)


def process_async_message(name, last_name, phone_number, email, content):
    with app.app_context():
        new_message = MessageModel(name=name, last_name=last_name,
                                phone_number=phone_number, email=email,
                                content=content)
        db.session.add(new_message)
        db.session.commit()

@app.route('/add_message_async/', methods=['GET', 'POST'])
def add_message_async():
    print(request.method)
    if request.method == 'GET':
        form = MessageForm()
        print("form sent")
        return render_template('add_message_async.html', form=form)
    
    elif request.method == 'POST':
        print("got a POST request")
        form = MessageForm(request.form)
        if form.validate():
            t = multiprocessing.Process(target=process_async_message, args=(form.name.data, form.last_name.data,
                                        form.phone_number.data, form.email.data,
                                        form.content.data))
            t.start()
            return jsonify({'message': 'Message sent asynchronously!'}), 200
        else:
            return jsonify({'errors': form.errors}), 400
        
    return 'Method Not Allowed', 405

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
