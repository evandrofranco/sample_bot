import requests
import json
import os

READMINE_PAGE = 'http://{}/issues'.format(os.environ.get('READMINE_IP'))
DATA = dict({"issue": {"project_id": 1, "priority_id": 4, "tracker_id": 1}})


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
        DATA.get("issue").update({"subject": data.lstrip()})
        body = json.dumps(DATA)
        print(body)
        response = requests.post(url=self.get_app_url(
            'POST'), headers=self.define_header(), data=body)
        print(response)
        return response.json()


'''
if __name__ == "__main__":
    red = Redmine()
    ret = red.execute_post("Exemplo de bug")
    input = red.execute_get(1)
    print(input)
'''
