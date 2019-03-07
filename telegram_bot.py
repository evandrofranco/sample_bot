import json
import os
import sys
import requests
import telegram
import re

OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps('ok')
}
ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('Ocorreu um erro!')
}


def configure_telegram():
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    return telegram.Bot(TELEGRAM_TOKEN)


def publish_telegram_msg(event, context):

    bot = configure_telegram()

    if event.get('httpMethod') == 'POST' and event.get('body'):
        update = telegram.Update.de_json(json.loads(event.get('body')), bot)
        print(update)
        chat_id = update.message.chat.id
        text = update.message.text
        name = update.message.from_user.first_name

        response = create_msg_response(text, name)
        if response != '':
            bot.sendMessage(chat_id=chat_id, text=response)
            return OK_RESPONSE

    return ERROR_RESPONSE


def create_msg_response(input, first_name):
    response = ''
    if "ajuda" in input.lower():
        response = "Olá {}, sou um bot da Sempre IT!!\n".format(first_name)
        response += "Estou aqui para o que precisar, basta me chamar."
    elif "oi" in input.lower() or "/olá" in input.lower():
        response = "Olá {}, sou um bot da Sempre IT!!\n".format(first_name)
    elif "cep" in input.lower():
        response = get_endereco(input)
    return response


def get_endereco(input):
    ret = ''
    cep = tratar_endereco(input)
    if cep != -1:
        url = 'https://viacep.com.br/ws/{}/json/'.format(cep)
        r = requests.get(url)
        endereco = r.json()
        ret = "Você pesquisou pela rua {} no bairro {} da cidade {}.".format(
            endereco.get('logradouro'),endereco.get('bairro'),
            endereco.get('localidade')
        )
    else:
        ret = 'Não foi possível obter o CEP.'
    return ret


def tratar_endereco(msg):
    ret = ''
    msg = msg.replace('-', '')
    response = re.findall("[0-9]{8}", msg)
    if len(response) > 0:
        ret = response[0]
    else:
        ret = -1
    return ret
