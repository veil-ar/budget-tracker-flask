from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Transaction

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # change this later
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        t_type = request.form.get('type')  # 'income' or 'expense'
        new_transaction = Transaction(amount=amount, category=category, type=t_type, user_id=current_user.id)
        db.session.add(new_transaction)
        db.session.commit()
        flash('Transaction added!', 'success')
        return redirect(url_for('dashboard'))

    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expense
    return render_template('dashboard.html', transactions=transactions, total_income=total_income, total_expense=total_expense, balance=balance)
    



    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expense
    return render_template('dashboard.html', transactions=transactions, total_income=total_income, total_expense=total_expense, balance=balance)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
