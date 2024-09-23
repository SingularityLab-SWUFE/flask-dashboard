from flask import request, render_template
import requests as req
from ..models import db, User, Assignment, Submission
from ..utils import Validator
from . import pages


@pages.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@pages.route('/rank', methods=['GET'])
def test():
    assignment_id = request.args.get('assignment_id')
    api_resp = req.request('GET', 'http://localhost:5000/api/scoreboard',
                           params={'assignment_id': assignment_id})
    data = api_resp.json()
    if data['code'] == 200:
        return render_template('rank.html', data=data['data'])
    else:
        return render_template('error.html', error_msg=data['msg'])
