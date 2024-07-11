from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
import re
from . import account
from ..models import db, User
from ..utils import Result, Validator


class RegisterValidator(Validator):
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def validate(self):
        is_valid, error_msg = True, ""

        if not self.username:
            is_valid, error_msg = False, "username is required"
        if not self.password:
            is_valid, error_msg = False, "password is required"
        # TODO: add more validation rules for password

        if not self.email:
            is_valid, error_msg = False, "email is required"

        EMAIL_REGEX = r'^[\w\-\.]+@([\w-]+\.)+[\w-]{2,}$'
        if not re.match(EMAIL_REGEX, self.email):
            is_valid, error_msg = False, "invalid email format"

        if User.query.filter_by(email=self.email).first():
            is_valid, error_msg = False, "email already exists"

        return is_valid, error_msg


@account.route('/register', methods=['POST'])
def register():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    validator = RegisterValidator(username, password, email)
    is_valid, error_msg = validator.validate()

    if not is_valid:
        return Result.error(msg=error_msg)

    new_user = User(
        username=username,
        password_hash=generate_password_hash(password),
        email=email,
    )
    db.session.add(new_user)
    db.session.commit()

    return Result.success(data={"user": new_user.to_json()})


@account.route('/login', methods=['POST'])
def login():
    pass


@account.route('/test', methods=['GET'])
def test():
    return "test"
