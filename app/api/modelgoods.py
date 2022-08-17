from flask import jsonify
from sqlalchemy import or_
from sqlalchemy.orm import Bundle

import config
from app.api import bp
from app import db, libc
from app.models import Modelgood, Storage, Vollink, Vol, Folder
from config import Config


@bp.route('/modelgoods/<string:id>', methods=['GET'])
def get_model_by_id(id):
    return jsonify(db.session.query(Modelgood).get_or_404(id).to_dict())

@bp.route('/modelgoods/search/<string:searchtext>', methods=['GET'])
def get_models_by_id(searchtext):
    basequery=db.session.query(Storage,Modelgood, Vollink,Vol,Folder).\
            join(Modelgood,Storage.modelid == Modelgood.id).\
            join(Folder, Storage.folderid == Folder.id).\
            join(Vollink,Modelgood.id==Vollink.modelid).\
            join(Vol, Vollink.vol1id==Vol.id).\
            filter(Vollink.level=='1'). \
            filter(Storage.folderid != '0rfarg000os1'). \
            filter(Storage.folderid != '0rfarg000FZh')
    if " " in searchtext:
     for search in searchtext.split(' '):
         search_args = [col.ilike('%%%s%%' % search) for col in [Modelgood.name, Vollink.barcode]]
         basequery=basequery.filter(or_(*search_args))
    else:
        search_args=[col.ilike('%%%s%%' % searchtext) for col in [Modelgood.name, Vollink.barcode]]
        basequery = basequery.filter(or_(*search_args))
    list=[(s.to_dict(),m.to_dict(),v.to_dict(),vl.to_dict(),fl.to_dict(),
           {"imageurl":"http://"+config.Config.serverdb+'''/img/'''+m.imagename() if m.imagename() else None}) for s,m,v,vl,fl in
        basequery.\
        # filter(Modelgood.name.ilike(f'%{searchtext}%')).\
                   all()]
    return jsonify(list)
