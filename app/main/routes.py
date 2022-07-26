# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for
from sqlalchemy.orm import load_only

from  config import Config
from app import db
from app.main.form import LoginForm, DocFileForm
from flask_login import current_user, login_user, login_required
from app.models import User, Modelgood, Pricelink, Servicedict, Typeservice, Storage, Folder, Vollink, Vol
from app.main import bp

def FindModel(searchtext=""):

    if searchtext:
        sql_add = ''
        searchlist = []
        if " " in searchtext:
            for text in searchtext.split():
                sql_add += ''' and ( (upper(mg."name"||'|'||mg."comment") containing ?) )'''
                searchlist.append(text)

        else:
            sql_add += ''' and ( (upper(mg."name"||'|'||mg."comment") containing ?) )'''
            searchlist.append(searchtext)
        if isinstance(searchtext, int):
            sql_add += '''' and ( (upper(v."codemodel"||'|'||v."barcode") containing ?) )'''
            searchlist.append(searchtext)

        sql = f'''
        select  First 10  
          mg."id" "modelid",
          max(mg."name"),

          LIST('на складе: '||f."name"||' - '||s."count"||' условная единица\n') "scount",

           MAX( (dec64i0(mg."id")||'_'||dec64i1(mg."id")||'.'||mg."imgext")) "image",
           MAX(s."p2value") price

          FROM "modelgoods" as mg
          left outer join "vollink" v on (mg."id"=v."modelid")
          left outer join "storage" s on (s."modelid" = mg."id")
          left outer join "folders" f on (s."folderid" = f."id")
          where
          s."count" >0.0 and s."count"  is not null
          {sql_add}
          and (
          s."folderid"='0rfarg00002C'
            or     s."folderid"='0000010004cx'
            or     s."folderid"='0000010004Xu'
            or     s."folderid"='0rfarg000b52'   )
          and  v."level"=1.0                group by mg."id"

        '''



@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@bp.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    form = DocFileForm()

    modelgoods = db.session.query(Storage,Modelgood, Vollink,Vol,Folder).\
        join(Modelgood,Storage.modelid == Modelgood.id).\
        join(Folder, Storage.folderid == Folder.id).\
        join(Vollink,Modelgood.id==Vollink.modelid).\
        join(Vol, Vollink.vol1id==Vol.id). \
        options(load_only(Storage.count, Storage.p2value, Modelgood.name, Modelgood.imgext,
                 Vollink.barcode, Vollink.kmin, Vollink.codemodel, Vol.name, Folder.name)). \
        filter(Vollink.level=='1').\
        paginate(page,
                                                    Config.MODELGOODS_PER_PAGE,
                                                    False).items
    print(modelgoods)
    if form.validate_on_submit():
        return "Filename"
        # filename = images.save(form.docFileField.data)
        # return f'Filename: {filename}'

    return render_template('index.html', form=form, modelgoods=modelgoods)



@bp.route('/services/')
def servises():
        iservises = db.session.query(Pricelink).join(Servicedict, Servicedict.id==Pricelink.modelid).join(Typeservice,
                                                                                                          Servicedict.typeid==Typeservice.id).add_columns(Pricelink.p2value, Servicedict.name)

        return render_template('servises.html',servises=iservises)


@bp.route('/admin/')
@login_required
def admin():
    return render_template('admin.html')


@bp.route('/login/', methods=['post', 'get'])
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


@bp.route('/logout/')
@login_required
def logout():
    flash("You have been logged out.")
    return redirect(url_for('login'))


# @app.route('/modelgoods/search/<searchtext>')
# def get(searchtext):
#         #print("ищем товар на складе %s"%searchtext)
#         modelgoods = db.session.query(Storage, Modelgood, Vollink, Vol, Folder). \
#             join(Modelgood, Storage.modelid == Modelgood.id). \
#             join(Folder, Storage.folderid == Folder.id). \
#             join(Vollink, Modelgood.id == Vollink.modelid). \
#             join(Vol, Vollink.vol1id == Vol.id). \
#             filter(Vollink.level == '1'). \
#             filter(Modelgood.name.like(f'%{searchtext}%')). \
#             items
#         return Response(json.dumps(FindModel(searchtext=searchtext), ensure_ascii=False).encode('utf-8'),  mimetype='application/json')