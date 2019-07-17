import os
import json
import requests
from requests.status_codes import codes
from .models import Clube, Time, Liga, Partida
from .error import CartolaError


class Cartola(object):
    def __init__(self, email=None, password=None):
        self._api_url = 'https://api.cartolafc.globo.com'
        self._email = email
        self._password = password

        if bool(email) != bool(password):
            raise CartolaError('E-mail ou senha ausente')
        elif all((email, password)):
            self.set_credentials(email, password)

    def set_credentials(self, email, password):
        self._email = email
        self._password = password
        response = requests.post(self._auth_url, json=dict(payload=dict(
            email=self._email, password=self._password, serviceId=4728)))
        body = response.json()
        print(body)
        if response.status_code == codes.ok:
            self._glb_id = body['glbId']
        else:
            raise CartolaError(body['userMessage'])

    def _request(self, url, params=None):
        try:
            response = requests.get(url, params=params)
            parsed = json.loads(response.content.decode('utf-8'))
            return parsed
        except CartolaError as err:
            raise err

    def clubes(self):
        url = '{api_url}/clubes'.format(api_url=self._api_url)
        data = self._request(url)
        return {int(clube_id): Clube.from_dict(clube) for clube_id,
                clube in data.items()}

    def ligas(self, query):
        url = '{api_url}/ligas'.format(api_url=self._api_url)
        data = self._request(url, params=dict(q=query))
        return [Liga.from_dict(liga_info) for liga_info in data]

    def partidas(self, rodada):
        url = '{api_url}/partidas/{rodada}'.format(
            api_url=self._api_url, rodada=rodada)
        data = self._request(url)
        clubes = {clube['id']: Clube.from_dict(
            clube) for clube in data['clubes'].values()}
        return sorted([Partida.from_dict(partida, clubes=clubes)
                       for partida in data['partidas']], key=lambda p: p.data)


'''
if __name__ == "__main__":
    # cartola = Cartola()
    # print(cartola.ligas('ete old'))
    # print(cartola.partidas(1))
    cartola = Cartola()
    ligas = cartola.ligas('globo999')
    resp = 'Foram encontradas {} Ligas! \n'.format(len(ligas))
    for liga in ligas:
        resp += '* {} \n\t - descrição: {} \n'.format(
            liga.nome, liga.descricao)
    print(resp)
'''
