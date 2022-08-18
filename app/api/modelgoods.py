from flask import jsonify

from sqlalchemy import or_, func

import config
from app import db, dec64, cache
from app.api import bp
from app.models import Modelgood, Storage, Vollink, Vol, Folder
from config import Config


@bp.route('/modelgoods/<string:id>', methods=['GET'])
def get_model_by_id(id):
    return jsonify(db.session.query(Modelgood).get_or_404(id).to_dict())


@bp.route('/modelgoods/search/<string:search_text>', methods=['GET'])

def get_models_by_id(search_text):
    if len(search_text) > 3:
        base_query = db.session.query(func.sum(Storage.count),func.max(Storage.p2value), func.max(Modelgood.name),func.max(Modelgood.id),func.max(Modelgood.imgext),
            func.max(Vollink.barcode),func.max(Vollink.codemodel),func.max(Vollink.kmin),func.max(Vol.name).label("Volname"), func.list(Folder.name).label('Foldername')).\
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
        foo=base_query.paginate(1,
                                            Config.MODELGOODS_PER_PAGE,
                                            False).items
        if foo is not None:
            cache.set("foo", foo)
        bar = cache.get("foo")
        list_to_json = {'storage':[{"count":sc/vkmin,"price":int(sp*vkmin), 'name':mn, 'id':mi, 'barcde':vb,'code':vc.strip(),'volname':vn.strip(),"foldername":fn,
                        "img_url": "http://" + config.Config.serverdb + '''/img/''' + (dec64(mi)+'.'+mimext) if
                        mimext else None}
                        for sc,sp, mn, mi,mimext, vb,vc,vkmin,vn,fn in
                        bar]}
        return jsonify(list_to_json)
