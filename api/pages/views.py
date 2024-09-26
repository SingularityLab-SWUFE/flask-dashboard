from flask import request, render_template, redirect, url_for, session
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


@pages.route('/authorize', methods=['GET', 'POST'])
def not_authorized():
    if request.method == 'POST':
        token = request.form.get('token')
        user = User.query.filter_by(access_token=token).first()
        if not user:
            return render_template('error.html', error_msg='User not found or invalid token')
        if user.role != 'admin':
            return render_template('error.html', error_msg='Permission denied')
        else:
            session['token'] = token
            return f"authorized token: {token}"
    return render_template('authorize.html')


@pages.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        token = session.get('token')
        assignment_id = request.form.get('assignment_id')
        api_resp = req.request('POST', 'http://localhost:5000/api/testcases',
                               files={'testcases': file},
                               data={'assignment_id': assignment_id},
                               headers={'Authorization': f'Bearer {token}'})
        data = api_resp.json()
        if data['code'] == 200:
            return redirect(url_for('pages.upload'))
        else:
            return render_template('error.html', error_msg=data['msg'])

    assignments = Assignment.query.all()
    return render_template('upload.html', assignments=assignments)

@pages.route('/assignment', methods=['GET', 'POST'])
def assignment():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        max_score = request.form.get('max_score')
        deadline = request.form.get('deadline')
        token = session.get('token')
        api_resp = req.request('POST', 'http://localhost:5000/api/assignment',
                               data={'name': name, 'description': description, 'max_score': max_score, 'deadline': deadline},
                               headers={'Authorization': f'Bearer {token}'})
        data = api_resp.json()
        if data['code'] == 200:
            return redirect(url_for('pages.upload'))
        else:
            return render_template('error.html', error_msg=data['msg'])
    
    return render_template('assignment.html')