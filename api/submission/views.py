from datetime import datetime, timezone

from flask import request
from sqlalchemy import func

from . import submission
from ..models import db, User, Submission, Assignment, Testcase
from ..utils import Result, Validator, token_required


class AssignmentValidator(Validator):
    def __init__(self, name, description, max_score, deadline):
        self.name = name
        self.description = description
        self.max_score = max_score
        self.deadline = deadline

    def validate(self):
        is_valid, error_msg = True, ''
        if len(self.name) == 0:
            is_valid, error_msg = False, 'Assignment name is required'
        if self.deadline and self.deadline <= datetime.now():
            is_valid, error_msg = False, 'Deadline must be in the future'
        return is_valid, error_msg


class SubmissionValidator(Validator):
    def __init__(self, assignment_id, score):
        self.assignment_id = assignment_id
        self.score = score

    def validate(self):
        is_valid, error_msg = True, ''
        assignment = Assignment.query.filter_by(id=self.assignment_id).first()
        if not assignment:
            is_valid, error_msg = False, f'Assignment {
                self.assignment_id} not found'
        if not self.score:
            is_valid, error_msg = False, 'Score is required'
        if int(self.score) > assignment.max_score:
            is_valid, error_msg = False, f'Score cannot be greater than {
                assignment.max_score}'
        if datetime.now() > assignment.deadline:
            is_valid, error_msg = False, 'Deadline has passed'
        return is_valid, error_msg


@submission.route('/submission', methods=['GET', 'POST'])
@token_required
def submit(user):
    data = request.form
    assignment_id = data.get('assignment_id')
    score = data.get('score')

    # TODO: validate md5 of test file
    validator = SubmissionValidator(assignment_id, score)
    is_valid, error_msg = validator.validate()
    if not is_valid:
        return Result.error(error_msg)

    submission = Submission(user_id=user.id, assignment_id=assignment_id,
                            content=data.get('content'), score=int(score))
    db.session.add(submission)
    db.session.commit()
    return Result.success(f'Submission {submission.id} created successfully at {submission.submitted_at}')


@submission.route('/submission', methods=['GET'])
def user_submissions():
    data = request.args
    user_id = data.get('user_id')
    assignment_id = data.get('assignment_id')
    if not user_id or not assignment_id:
        return Result.error('User id and assignment id are required')
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return Result.error(f'User {user_id} not found')
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if not assignment:
        return Result.error(f'Assignment {assignment_id} not found')
    submissions = Submission.query.filter_by(
        user_id=user_id, assignment_id=assignment_id).all()
    return Result.success(data=[s.to_json() for s in submissions])
    

@submission.route('/assignment', methods=['GET', 'POST'])
@token_required
def assign(user : User):
    if user.role != 'admin':
        return Result.error('Permission denied')

    data = request.form
    name = data.get('name')
    description = data.get('description')
    max_score = data.get('max_score')
    deadline = data.get('deadline')
    deadline = datetime.strptime(
        deadline, '%Y-%m-%dT%H:%M') if deadline else None

    validator = AssignmentValidator(name, description, max_score, deadline)
    is_valid, error_msg = validator.validate()
    if not is_valid:
        return Result.error(error_msg)

    assignment = Assignment(name=name, description=description,
                            max_score=max_score, deadline=deadline, is_published=True)
    db.session.add(assignment)
    db.session.commit()
    return Result.success(f'Assignment {assignment.id} created successfully at {assignment.created_at}')


@submission.route('/assignment', methods=['GET'])
def assignment_info():
    data = request.args
    assignment_id = data.get('assignment_id')
    if not assignment_id:
        return Result.error('Assignment id is required')
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if not assignment:
        return Result.error(f'Assignment {assignment_id} not found')
    return Result.success(data=assignment.to_json())

@submission.route('/scoreboard', methods=['GET'])
def scoreboard():
    data = request.args
    assignment_id = data.get('assignment_id')
    if not assignment_id:
        return Result.error('Assignment id is required')
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if not assignment:
        return Result.error(f'Assignment {assignment_id} not found')

    subquery = (
        db.session.query(
            Submission.user_id,
            func.max(Submission.score).label('max_score'),
            func.min(Submission.submitted_at).label('earliest_submission')
        )
        .filter_by(assignment_id=assignment_id)
        .group_by(Submission.user_id)
        .subquery()
    )
    scoreboard = (
        db.session.query(
            User.username,
            subquery.c.max_score,
            subquery.c.earliest_submission
        )
        .join(User, User.id == subquery.c.user_id)
        .order_by(subquery.c.max_score.desc(), subquery.c.earliest_submission.asc())
        .all()
    )
    data = {"assignment": {
        "name": assignment.name,
        "description": assignment.description,
        "max_score": assignment.max_score,
        "deadline": assignment.deadline
    },
        "scoreboard": [{'username': s[0], 'score': s[1],
                        'submission_time': s[2]} for s in scoreboard]
    }
    return Result.success(data=data)


@submission.route('/testcases', methods=['POST'])
@token_required
def upload_testcase(user: User):
    if user.role != 'admin':
        return Result.error('Permission denied')

    data = request.form
    assignment_id = data.get('assignment_id')
    if not assignment_id:
        return Result.error('Assignment id is required')
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if not assignment:
        return Result.error(f'Assignment {assignment_id} not found')
    testcases = request.files.getlist('testcases')
    if not testcases:
        return Result.error('No files part')
    for testcase in testcases:
        existing_testcase = Testcase.query.filter_by(
            file_name=testcase.filename, assignment_id=assignment_id).first()
        if existing_testcase:
            # overwrite it
            existing_testcase.content = testcase.read()
        else:
            obj = Testcase(file_name=testcase.filename,
                       content=testcase.read(), assignment_id=assignment_id)
            db.session.add(obj)

    db.session.commit()
    return Result.success(f'{len(testcases)} testcases uploaded successfully.')


@submission.route('/md5/<int:assignment_id>', methods=['GET'])
def validate_md5(assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if not assignment:
        return Result.error(f'Assignment {assignment_id} not found')
    data = request.form
    client_md5 = data.get('md5')
    type = data.get('type')
    if not type:
        return Result.error('File type is required')
    if not client_md5:
        return Result.error('Client MD5 is required')

    server_md5 = ''
    if type == 'json':
        server_md5 = assignment.lab_config_md5()
        if client_md5 == server_md5:
            return Result.success(data=True)
        else:
            return Result.error(f'{type} MD5 does not match server ')
    elif type == 'py':
        server_md5 = [
            testcase for testcase in assignment.testcases if testcase.get_md5() == client_md5]
        if server_md5:
            return Result.success(data=True)
        else:
            return Result.error(f'{type} MD5 does not match server ')
    else:
        return Result.error('Invalid file type')
