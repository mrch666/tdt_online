from flask import jsonify

from app.api import bp
from app import db
from app.models import Modelgood, Storage, Vollink, Vol, Folder
from config import Config


@bp.route('/modelgoods/<string:id>', methods=['GET'])
def get_model_by_id(id):
    return jsonify(db.session.query(Modelgood).get_or_404(id).to_dict())

@bp.route('/modelgoods/search/<string:searchtext>', methods=['GET'])
def get_models_by_id(searchtext):
    return jsonify(db.session.query(Storage,Modelgood, Vollink,Vol,Folder).\
        join(Modelgood,Storage.modelid == Modelgood.id).\
        join(Folder, Storage.folderid == Folder.id).\
        join(Vollink,Modelgood.id==Vollink.modelid).\
        join(Vol, Vollink.vol1id==Vol.id).\
        filter(Vollink.level=='1'). \
                   filter(Modelgood.name.like(f'%{searchtext}%')).\
                   paginate(1,Config.MODELGOODS_PER_PAGE,
                            False).\
                   items)