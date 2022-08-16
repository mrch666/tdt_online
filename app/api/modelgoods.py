from flask import jsonify

from app.api import bp
from app.models import Modelgood

@bp.route('/modelgoods/<string:id>', methods=['GET'])
def get_model_by_id(id):
    return jsonify(Modelgood.query.get_or_404(id).to_dict())

@bp.route('/modelgoods/search/<string:searchtext>', methods=['GET'])
def get_models_by_id(searchtext):
    return jsonify(Modelgood.query.get_or_404(searchtext).to_dict())