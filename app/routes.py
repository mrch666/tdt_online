# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse

from  config import Config
from app import app , db
from app.form import LoginForm, DocFileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Modelgood, Pricelink, Servicedict, Typeservice



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    form = DocFileForm()
    modelgoods = db.session.query(Modelgood).order_by(Modelgood.changedate.desc()).paginate(page, Config.MODELGOODS_PER_PAGE,
                                                                                            False).items
    if form.validate_on_submit():
        return "Filename"
        # filename = images.save(form.docFileField.data)
        # return f'Filename: {filename}'

    return render_template('index.html', form=form, modelgoods=modelgoods)



@app.route('/services/')
def servises():
        iservises = db.session.query(Pricelink).join(Servicedict, Servicedict.id==Pricelink.modelid).join(Typeservice,
                                                                                                          Servicedict.typeid==Typeservice.id).add_columns(Pricelink.p2value, Servicedict.name)

        return render_template('servises.html',servises=iservises)


@app.route('/admin/')
@login_required
def admin():
    return render_template('admin.html')


@app.route('/login/', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            print(user.username, user.password)
            login_user(user, remember=form.remember.data)
            return redirect(url_for('admin'))

        else:
            flash("Invalid username/password", 'error')
            return redirect(url_for('login'))
    else:
        return render_template('login.html', form=form)


@app.route('/logout/')
@login_required
def logout():
    flash("You have been logged out.")
    return redirect(url_for('login'))

