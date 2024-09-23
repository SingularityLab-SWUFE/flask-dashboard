from flask import Blueprint

submission = Blueprint('submission', __name__, url_prefix='/api')

from . import views