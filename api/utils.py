from flask import jsonify
from abc import abstractmethod
from typing import Tuple

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
        return jsonify(resp)

    @staticmethod
    def error(msg="error"):
        resp = {
            "code": 400,
            "msg": msg,
        }
        return jsonify(resp)
