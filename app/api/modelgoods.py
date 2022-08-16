from flask import jsonify

from app.api import bp
from app.models import Modelgood

@bp.route('/modelgoods/<str:id>', methods=['GET'])
def get_user(id):
    return jsonify(Modelgood.query.get_or_404(id).to_dict())

@bp.route('/modelgoods/search/<str:searchtext>', methods=['GET'])
def get_user(id):
    return jsonify(Modelgood.query.get_or_404(id).to_dict())