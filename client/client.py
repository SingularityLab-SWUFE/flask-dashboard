import unittest
import os
import io
import requests
import datetime
from datetime import datetime
import getpass
import glob
import json
import sys
import hashlib
import readline

assert sys.version_info >= (3, 12), 'Python version should be 3.12 or higher.'

# for local server
DEST_URL = 'http://localhost:5000'
VERSION = '0.1.0'
history_file = '.history'


# utils
class UnittestHandler():
    def __init__(self, base_dirs=['.']):
        '''
            Specify the directories where the test files are located.
            Subdirectories will be searched recursively.
        '''
        self.test_file_dirs = base_dirs
        self.splitor = "=" * 50
        self.total_tests = 0
        self.passed_tests = 0
        self.test_output = ''

    def test_single(self, base_dir, testcases=[]):
        '''
            Running tests for a single lab assignment.
            If testcases is specified, only those testcases will be run.
        '''
        print(f'Running tests in {base_dir}')
        print(self.splitor)
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        # if provided test files
        if testcases:
            for testcase in testcases:
                suite.addTests(loader.discover(base_dir, testcase))
        # find all `test_*.py` files in `base_dir`
        else:
            suite = loader.discover(base_dir)

        runner = unittest.TextTestRunner(
            stream=io.StringIO(), resultclass=unittest.TextTestResult, verbosity=2)
        result = runner.run(suite)

        if result.failures or result.errors:
            for failure_test, traceback in result.failures:
                print(f'\033[33m[FAILED]\033[0m Test {failure_test} failed with traceback:\n{
                    traceback}')
            for error_test, traceback in result.errors:
                print(f'\033[33m[ERROR]\033[0mTest {
                      error_test} failed with traceback:\n{traceback}')

        self.total_tests += result.testsRun
        self.passed_tests += result.testsRun - \
            len(result.failures) - len(result.errors)

    def test_all(self):
        '''
            Running tests for all lab assignments.
        '''
        for test_file_dir in self.test_file_dirs:
            self.test_single(test_file_dir)


def to_md5(data: dict):
    '''
        Convert a dict object to jsonified string md5 hash.
    '''
    return hashlib.md5(json.dumps(data).encode()).hexdigest()


class ScoreClient():

    def __init__(self, url):
        self.url = url
        self.logined = False
        self.username = None
        self.submit_to_server = True
        self.lab_config = []

    def register(self, email, username, password):
        resp = requests.request('POST', self.url + '/api/register',
                                data={'email': email, 'username': username, 'password': password})
        if resp.status_code == 200:
            print('Registration successful. Now you can login with your credentials!')
        else:
            print(resp.json()['msg'])

    def login(self, username, password):
        resp = requests.request('POST', self.url + '/api/login',
                                data={'username': username, 'password': password})
        if resp.status_code == 200:
            data = resp.json()['data']
            api_token = data['access_token']
            username = data['user']['username']

            self.logined = True
            self.username = username

            # store the API token in the environment variable
            os.environ['SCOREBOARD_API_TOKEN'] = api_token
            print(f'Login successful. Hello {username}!')

            if '--show-token' in sys.argv:
                print(f'Your API token is: {api_token}')
                print('\033[91m' + 'Warning: Do NOT share or expose your API token! \nAPI tokens are sensitive and provide full access to your account.\nAnyone with access to your token can perform actions on your behalf, which could result in data loss, account compromise, or unexpected charges. ' + '\033[0m')
        else:
            print(resp.json()['msg'])

    def logout(self):
        if not self.logined:
            print('You are not logged in.')
            return

        os.environ.pop('SCOREBOARD_API_TOKEN', None)
        client.logined = False
        client.username = None
        print('Logout successful.')

    def parsing_lab_config(self):
        '''
            Discover all `*.json` files in the current directory and return deserialized data of lab config.
        '''
        lab_config = glob.glob('lab*.json')
        if not lab_config:
            print('No lab configuration file found. Please check whether you are in the correct directory or missing current lab configuration file.')
            return
        if len(lab_config) > 1:
            print('Multiple lab configuration files were found:')
            for config in lab_config:
                print(config)
        for lab_config_file in lab_config:
            with open(lab_config_file) as f:
                data = json.load(f)
                self.lab_config.append(data)
        print(self.lab_config)

    def test(self, assignment_id):
        '''
            Test for a single lab assignment.
        '''
        lab_config = None
        for config in self.lab_config:
            if int(assignment_id) == int(config['assignment_id']):
                lab_config = config
        base_dir = lab_config['base_dir']
        testcases = lab_config["test_cases"]
        handler = UnittestHandler(base_dirs=['.'])
        handler.test_single(base_dir, testcases)
        # handler.test_all()

        local_score = int(handler.passed_tests /
                          handler.total_tests * lab_config['max_score'])
        print(f'Your local score for assignment {
            lab_config["name"]} is {local_score}/{lab_config["max_score"]}.')
        return local_score

    def submit(self, assignment_id):
        score = self.test(assignment_id)

        if self.submit_to_server:
            if not self.logined:
                print('You are not logged in. Please login first before making submission.')
                return
            access_token = os.environ.get('SCOREBOARD_API_TOKEN')

            if not self.validate_config(assignment_id):
                print(
                    'Validation failed. Please check your lab configuration files and testcase files.')
                return

            resp = requests.request('POST', self.url + f'/api/submission',
                                    data={'assignment_id': assignment_id,
                                          'score': score},
                                    headers={'Authorization': f'Bearer {access_token}'})
            if resp.status_code == 200:
                print('Score submitted successfully!')
            else:
                print('Submission failed. ' + resp.json()['msg'])
                print(
                    '\033[33mIf you are supposed to submit to the server scoreboard, please check the failing message from server and try again.\033[0m')

    def submit_all(self):
        for config in self.lab_config:
            assignment_id = config['assignment_id']
            self.submit(assignment_id)
    
    def _validate_config(self, assignment_id, config_md5, type) -> bool:
        '''
            Validate the lab configuration file md5 with the server.
            Config includes the `*.json` file and testcase files `test_*.py`.
            File type can be 'json' or 'py'.
        '''
        resp = requests.request(
            'GET', self.url + f'/api/md5/{assignment_id}', data={'md5': config_md5, 'type': type})
        if resp.status_code == 200 and resp.json()['data']:
            return True
        else:
            print(f'Validation failed. Message: \033[33m{
                  resp.json()['msg']}\033[0m')
            return False

    def validate_config(self, assignment_id) -> bool:
        '''
            Validate lab configuration files (in the current directory) and related testcase files.
        '''
        lab_config = None
        for config in self.lab_config:
            if int(assignment_id) == int(config['assignment_id']):
                lab_config = config
        if not lab_config:
            print('No lab configuration file found. Please check whether you are in the correct directory or missing current lab configuration file.')
            return False
        base_dir = lab_config['base_dir']
        testcase_dirs = [base_dir + '/' + testcase_dir for testcase_dir in lab_config['test_cases']]
        local_md5 = to_md5({k: v for k, v in lab_config.items() if k != 'base_dir'})
        if not self._validate_config(assignment_id, local_md5, 'json'):
            return False
        for testcase in testcase_dirs:
            with open(testcase) as f:
                testcase_data = f.read()
                testcase_md5 = hashlib.md5(
                    testcase_data.encode()).hexdigest()
                if not self._validate_config(assignment_id, testcase_md5, 'py'):
                    return False
        return True

    def scoreboard(self, assignment_id):
        '''
            CLI display the scoreboard of an assignment.
        '''
        resp = requests.request(
            'GET', self.url + f'/api/scoreboard', params={'assignment_id': assignment_id})
        if resp.status_code == 200:
            data = resp.json()['data']
            assignment = data['assignment']
            scoreboard = data['scoreboard']
            print(f'Assignment: {assignment["name"]}')
            print(f'score: {assignment["max_score"]} points')
            print(f'description: {assignment["description"]}')

            # if the assignment is due
            if datetime.strptime(assignment["deadline"], "%a, %d %b %Y %H:%M:%S %Z") < datetime.now():
                print(f'\033[31mDue Date: {assignment["deadline"]}\033[0m')
                print(
                    f'\033[31mThe assignment is over. You cannot submit any more scores.\033[0m')
            else:
                print(f'\033[33mDue Date: {assignment['deadline']}\033[0m')

            print(f'{"Rank":<10}{"Score":<10}{
                  "Username":<15}{"Submission Time":<25}')
            for rank, user in enumerate(scoreboard):
                print(
                    f'{rank+1:<10}{user["score"]:<10}{user["username"]:<15}{user["submission_time"]:<25}')
        else:
            print(resp.json()['msg'])


# Command line interface for the client
if __name__ == '__main__':
    client = ScoreClient(DEST_URL)

    # if --local option is provided, do not submit to the server
    if '--local' in sys.argv:
        print('\033[33mRunning in local mode. No submission to the server.\033[0m')
        client.submit_to_server = False

    print(f'Welcome to the Scoreboard CLI Client {VERSION}!')
    client.parsing_lab_config()
    
    if os.path.exists(history_file):
        readline.read_history_file(history_file)
        
    while True:
        cmd = input(f'{client.username if client.logined else ""}> ')
        readline.add_history(cmd)
        if cmd == 'register':
            email = input('Enter your email: ')
            username = input('Enter your username: ')
            password = getpass.getpass('Enter your password: ')
            client.register(email, username, password)
        elif cmd == 'login':
            username = input('Enter your username: ')
            password = getpass.getpass('Enter your password: ')
            client.login(username, password)
        elif cmd == 'logout':
            client.logout()
        elif cmd == 'submit':
            if len(client.lab_config) == 1:
                client.submit(client.lab_config[0]['assignment_id'])
            else:
                assignment_id = input('Enter the assignment ID: ')
                if not assignment_id:
                    client.submit_all()
                else:
                    client.submit(assignment_id)
        elif cmd == 'scoreboard':
            assignment_id = input('Enter the assignment ID: ')
            client.scoreboard(assignment_id)
        elif cmd == 'help':
            print('register: register a new account')
            print('login: login to your account')
            print('logout: logout from your account')
            print('submit: submit your score to the server')
            print('scoreboard: view the scoreboard of an assignment')
            print('exit/quit/q: exit the client')
            print('help/h: show this help message')
        elif cmd == 'exit' or cmd == 'quit' or cmd == 'q':
            print('bye')
            break
        else:
            print(f'Invalid command of {cmd}.')
    readline.write_history_file(history_file)
