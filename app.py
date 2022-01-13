from flask import Flask, render_template, redirect, url_for, flash
from scripts.forms import SignUpForm, LoginForm
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY']= 'test'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap(app)


@app.route('/', methods = ['GET', 'POST'])
def index():
    #form = SignUpForm() 
    login_form = LoginForm()

    return render_template("index.html", login_form=login_form)

@app.route('/register', methods=['POST','GET'])
def register():
    form = SignUpForm() 
    #login_form = LoginForm()

    if form.validate_on_submit():
        user = User(username = form.username.data, password_hash=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST'])
def login():
    form = SignUpForm() 
    login_form = LoginForm()

    if login_form.validate_on_submit() :
        user = User.query.filter_by(username=login_form.username.data).first()
        if not user or not check_password_hash(user.password_hash, login_form.password.data):
            flash('Please check your login details')
            redirect(url_for('index'))
        else:
            login_user(user)
            return redirect(url_for('showETFs'))
 
    return render_template("index.html", form=form, login_form=login_form)


@app.route('/user/<username>', methods=['GET','POST'])
def userpage(username):
    return f"You have successfully registered {username}!"

@app.route('/etfs', methods=['GET'])
@login_required
def showETFs():
    df = etfs.query.all()
    fav_list = favs.query.filter_by(user_id=current_user.id).all()
    fav_list = list(set([fav.etf_id for fav in fav_list]))
    return render_template('tables.html', data=df, fav_list = fav_list)

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
 
@app.route('/add/<int:etf_id>', methods=['POST'])
@login_required
def make_fav(etf_id):
    fav = favs(etf_id = etf_id, user_id = current_user.id)
    db.session.add(fav)
    db.session.commit()
    return redirect(url_for('showETFs')) 

@app.route('/my_etfs', methods=['GET'])
@login_required
def my_etfs():
    data = User.query.filter_by(id=current_user.id).first()
    my_list = [[fav.etfs.id, fav.etfs.name] for fav in data.faves]
    return render_template('my_etfs.html', data=my_list)

@app.route('/remove/<etf_id>', methods=['POST'])
@login_required
def remove_fav(etf_id):
    fav = favs.query.filter_by(etf_id = etf_id).filter_by(user_id=current_user.id).first()
    print(fav)
    db.session.delete(fav)
    db.session.commit()
    return redirect(url_for('my_etfs'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

def ingest_ETF():
    df = pd.read_csv('etfs.csv')
    for row in df.iterrows():
        etf = etfs(name=row[1]['Exposure'], Market=row[1]['Market'], ASX=row[1]['ASX Code'],iNAV=row[1]['iNAV'], Benchmark=row[1]['Benchmark'])
        db.session.add(etf)

    db.session.commit()

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    faves = db.relationship('favs', backref='user', lazy=True)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class favs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etf_id = db.Column(db.Integer, db.ForeignKey('etfs.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class etfs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    Market = db.Column(db.String(50))
    ASX = db.Column(db.String(10))
    iNAV = db.Column(db.String(30))
    Benchmark = db.Column(db.String(50))
    faves = db.relationship('favs', backref='etfs', lazy=True)
