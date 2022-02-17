from flask import render_template, redirect, url_for, request, flash, get_flashed_messages

from Market import app
from Market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from Market.models import Item, User
from flask_login import login_user, logout_user, login_required, current_user
from Market import db


@app.route('/')
@app.route('/home')
def home_page():  # put application's code here
    return render_template("home.html")


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_place():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        # Purchase Item Logic
        purchase_item = request.form.get("purchased_item")
        p_item = Item.query.filter_by(name=purchase_item).first()
        if p_item:
            if current_user.can_purchase(p_item):
                p_item.buy(current_user)
                flash(f"Congratulations! You purchased {p_item.name} for {p_item.price}", category='success')
            else:
                flash(f"Unfortunately, you dont have enough balance for {p_item.name}", category='danger')

        # Sold Item Logic
        sold_item = request.form.get('sold_item')
        s_item = Item.query.filter_by(name=sold_item).first()
        if s_item:
            if current_user.can_sell(s_item):
                s_item.sell(current_user)
                flash(f"Congratulations! You sold {s_item.name} back to market!", category='success')
            else:
                flash(f"Unfortunately, something went wrong with selling {p_item.name}", category='danger')

        return redirect(url_for('market_place'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)


@app.route('/register', methods=['POST', 'GET'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(name=form.name.data, username=form.username.data, email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}")

        return redirect(url_for('market_place'))

    if form.errors != {}:  # if the error dict is not empty
        for err_msg in form.errors.values():
            flash(f'{err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_place'))
        else:
            flash('Username or Password does not match! Please try again.', category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out!!", category='info')
    return redirect(url_for('home_page'))
