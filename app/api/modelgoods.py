from flask import jsonify

from app.api import bp
from app import db
from app.models import Modelgood

@bp.route('/modelgoods/<string:id>', methods=['GET'])
def get_model_by_id(id):
    return jsonify(db.session.query(Modelgood).query.get_or_404(id).to_dict())

@bp.route('/modelgoods/search/<string:searchtext>', methods=['GET'])
def get_models_by_id(searchtext):
    return jsonify(db.session.query(Modelgood).get_or_404(searchtext).to_dict())