from flask import jsonify
from sqlalchemy import or_
from sqlalchemy.orm import Bundle

from app.api import bp
from app import db
from app.models import Modelgood, Storage, Vollink, Vol, Folder
from config import Config


@bp.route('/modelgoods/<string:id>', methods=['GET'])
def get_model_by_id(id):
    return jsonify(db.session.query(Modelgood).get_or_404(id).to_dict())

@bp.route('/modelgoods/search/<string:searchtext>', methods=['GET'])
def get_models_by_id(searchtext):
    search_args=[col.ilike('%%%s%%' % searchtext) for col in [Modelgood.name, Vollink.barcode]]
    list=[(s.to_dict(),m.to_dict(),v.to_dict(),vl.to_dict(),fl.to_dict()) for s,m,v,vl,fl in db.session.query(Storage,Modelgood, Vollink,Vol,Folder).\
        join(Modelgood,Storage.modelid == Modelgood.id).\
        join(Folder, Storage.folderid == Folder.id).\
        join(Vollink,Modelgood.id==Vollink.modelid).\
        join(Vol, Vollink.vol1id==Vol.id).\
        filter(Vollink.level=='1'). \
        filter(Storage.folderid != '0rfarg000os1'). \
        filter(Storage.folderid != '0rfarg000FZh'). \
        filter(or_(*search_args)).\
        # filter(Modelgood.name.ilike(f'%{searchtext}%')).\
                   all()]
    return jsonify(list)


@bp.route('/modelgoods/imagebyid/<string:modelid>', methods=['GET'])
def get_image_by_id(modelid):
    res=db.session.execute('dec64i0', modelid).one()
    print(res)
    for r in res:
        print(r)
    return jsonify(res)