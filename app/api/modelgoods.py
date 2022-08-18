from flask import jsonify
from sqlalchemy import or_
from sqlalchemy.orm import load_only

import config
from app import db
from app.api import bp
from app.models import Modelgood, Storage, Vollink, Vol, Folder
from config import Config


@bp.route('/modelgoods/<string:id>', methods=['GET'])
def get_model_by_id(id):
    return jsonify(db.session.query(Modelgood).get_or_404(id).to_dict())


@bp.route('/modelgoods/search/<string:searched>', methods=['GET'])
def get_models_by_id(search_text):
    if len(search_text) > 3:
        base_query = db.session.query(Storage, Modelgood, Vollink, Vol, Folder). \
            join(Modelgood, Storage.modelid == Modelgood.id). \
            join(Folder, Storage.folderid == Folder.id). \
            join(Vollink, Modelgood.id == Vollink.modelid). \
            join(Vol, Vollink.vol1id == Vol.id). \
            options(load_only(Storage.count, Storage.p2value, Modelgood.name, Modelgood.imgext,
                              Vollink.barcode, Vollink.kmin, Vollink.codemodel, Vol.name, Folder.name)). \
            filter(Vollink.level == '1'). \
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
        list_to_json = [(s.to_dict(), m.to_dict(), v.to_dict(), vl.to_dict(), fl.to_dict(),
                         {
                             "img_url": "http://" + config.Config.serverdb + '''/img/''' + m.imagename() if
                             m.imagename() else None})
                        for s, m, v, vl, fl in
                        base_query.paginate(1,
                                            Config.MODELGOODS_PER_PAGE,
                                            False).items]
        return jsonify(list_to_json)
