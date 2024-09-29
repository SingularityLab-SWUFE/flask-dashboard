from flask import request, render_template, redirect, url_for, flash, session
import requests as req
from datetime import datetime
from ..models import db, User, Assignment, Submission
from ..utils import Validator
from . import pages


@pages.route('/', methods=['GET'])
def index():
    running_assignments = Assignment.query.filter(Assignment.deadline > datetime.now()).all()
    return render_template('index.html', assignments=running_assignments)


@pages.route('/rank', methods=['GET'])
def rank():
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
    next_url = request.args.get('next')
    if request.method == 'POST':
        token = request.form.get('token')
        user = User.query.filter_by(access_token=token).first()
        if not user:
            return render_template('error.html', error_msg='User not found or invalid token')
        if user.role != 'admin':
            return render_template('error.html', error_msg='Permission denied')
        else:
            session['token'] = token
            session['user'] = user.username
            return redirect(next_url or url_for('pages.index'))
    return render_template('authorize.html')


@pages.route('/upload', methods=['GET', 'POST'])
def upload():
    token = session.get('token')
    if not token:
        return redirect(url_for('pages.not_authorized', next=request.url))
    if request.method == 'POST':
        token = session.get('token')
        assignment_id = request.form.get('assignment_id')
        api_resp = req.request('POST', 'http://localhost:5000/api/testcases',
                               files=[('testcases', (file.filename, file.read()))
                                      for file in request.files.getlist('files')],
                               data={'assignment_id': assignment_id},
                               headers={'Authorization': f'Bearer {token}'})
        data = api_resp.json()
        if data['code'] == 200:
            flash(data['msg'], category='success')
            return redirect(url_for('pages.upload'))
        else:
            return render_template('error.html', error_msg=data['msg'])

    assignments = Assignment.query.all()
    return render_template('upload.html', assignments=assignments, user=session.get('user'))


@pages.route('/assignment', methods=['GET', 'POST'])
def assignment():
    token = session.get('token')
    if not token:
        return redirect(url_for('pages.not_authorized'))
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        max_score = request.form.get('max_score')
        deadline = request.form.get('deadline')
        token = session.get('token')
        api_resp = req.request('POST', 'http://localhost:5000/api/assignment',
                               data={'name': name, 'description': description,
                                     'max_score': max_score, 'deadline': deadline},
                               headers={'Authorization': f'Bearer {token}'})
        data = api_resp.json()
        if data['code'] == 200:
            return redirect(url_for('pages.upload'))
        else:
            return render_template('error.html', error_msg=data['msg'])

    return render_template('assignment.html', user=session.get('user'))


@pages.app_errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_msg='你来到了未知的领域'), 404