import requests
import os

READMINE_PAGE = 'http://3.14.69.84/issues'
DATA_PARAM_1 = '{"issue":{"project_id": 1,"subject": '
DATA_PARAM_2 = ',"priority_id": 4, "tracker_id": 1 }}'


class Redmine():

    def __init__(self):
        self._app_key = os.environ.get('READMINE_KEY_ID')
        self.url = ''

    def get_app_url(self, method, chamado=None):
        if method == 'GET':
            self.url = READMINE_PAGE + '/' + str(chamado) + '.json'
        else:
            self.url = READMINE_PAGE + '.json'
        return self.url

    def define_header(self):
        header = {"Content-Type": "application/json",
                  "X-Redmine-API-Key": self._app_key}
        return header

    def execute_get(self, chamado):
        response = requests.get(self.get_app_url(
            'GET', chamado), headers=self.define_header())
        return response.json()

    def execute_post(self, data):
        body = DATA_PARAM_1 + '"' + data + '"' + DATA_PARAM_2
        response = requests.post(self.get_app_url(
            'POST'), headers=self.define_header(), data=body)
        return response.json()


# red = Redmine()
# input = red.execute_get(1)
# print(resp)
# ret = red.execute_post("Exemplo de bug")
