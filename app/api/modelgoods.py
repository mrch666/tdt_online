from flask import jsonify
from sqlalchemy import or_, func

import config
from app import db
from app.api import bp
from app.models import Modelgood, Storage, Vollink, Vol, Folder
from config import Config


@bp.route('/modelgoods/<string:id>', methods=['GET'])
def get_model_by_id(id):
    return jsonify(db.session.query(Modelgood).get_or_404(id).to_dict())


@bp.route('/modelgoods/search/<string:search_text>', methods=['GET'])
def get_models_by_id(search_text):
    if len(search_text) > 3:
        base_query = db.session.query(func.sum(Storage.count),func.max(Storage.p2value), func.max(Modelgood.name),func.max(Modelgood.id),
            func.max(Vollink.barcode),func.max(Vollink.codemodel),func.max(Vol.name).label("Volname"), func.max(Folder.name).label('Foldername')).\
            join(Modelgood, Storage.modelid == Modelgood.id).\
            join(Folder, Storage.folderid == Folder.id).\
            join(Vollink, Modelgood.id == Vollink.modelid).join(Vol, Vollink.vol1id == Vol.id).group_by(Modelgood.id).\
            filter(Vollink.level == '1').\
            filter(Storage.folderid != '0rfarg000os1'). \
            filter(Storage.folderid != '0rfarg000FZh')
        if " " in search_text:
            for search in search_text.split(' '):
                if len(search) > 1:
                    search_args = [col.ilike('%%%s%%' % search) for col in [Modelgood.name, Vollink.barcode]]
                    base_query = base_query.filter(or_(*search_args))
        else:
            if len(search_text) > 3:
                search_args = [col.ilike('%%%s%%' % search_text) for col in [Modelgood.name, Vollink.barcode]]
                base_query = base_query.filter(or_(*search_args))
        list_to_json = base_query.paginate(1,Config.MODELGOODS_PER_PAGE,
                                            False).items
        return jsonify(list_to_json)
