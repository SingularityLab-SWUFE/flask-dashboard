from flask import jsonify, request
from abc import abstractmethod
from typing import Tuple
import functools
from .models import User


def token_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1]
        if not token:
            return Result.error('Authorization required')
        user = User.query.filter_by(access_token=token).first()
        if not user:
            return Result.error('Invalid token or user not found')
        
        return func(user, *args, **kwargs)

    return wrapper


class Validator:
    '''
        Interface for validator classes. Each validator class should implement the `validate` method.
    '''

    def __init__(self):
        pass

    @abstractmethod
    def validate(self) -> Tuple[bool, str]:
        '''
            Given specific validation rules, validate the input and return a tuple of `is_valid` and `error_msg`.
        '''
        pass


class Result:
    @staticmethod
    def success(msg="success", data=None):
        resp = {
            "code": 200,
            "msg": msg,
            "data": data
        }
        return jsonify(resp), 200

    @staticmethod
    def error(msg="error"):
        resp = {
            "code": 400,
            "msg": msg,
        }
        return jsonify(resp), 400
