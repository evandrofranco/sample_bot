import json
import os
import requests
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from conectors.luis_connector import LUISConnector
from api_calls.redmine import Redmine


IDLE, CRIAR_CHAMADO, CONSULTAR_CHAMADO_STATE = range(
    3)


OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps('ok')
}
ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('Ocorreu um erro!')
}

ABRIR_CHAMADO = 'Abrir Chamado'
CONSULTAR_CHAMADO = 'Consultar Chamado'
SAUDACAO = 'Saudacao'


def configure_telegram():
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    return telegram.Bot(TELEGRAM_TOKEN)


def error(bot, context):
    """Log Errors caused by Updates."""
    print('Update "%s" caused error "%s"', bot, context.error)


def publish_telegram_msg(event, context):

    bot = configure_telegram()
    if event.get('httpMethod') == 'POST' and event.get('body'):
        update = telegram.Update.de_json(json.loads(event.get('body')), bot)
        # print(update)
        chat_id = context.message.chat.id
        text = context.message.text
        name = context.message.from_user.first_name

        response = create_msg_response(text, name)
        if response != '':
            bot.sendMessage(chat_id=chat_id, text=response)
            return OK_RESPONSE

    return ERROR_RESPONSE


def control_flux(bot, context):
    response = ''
    intencao, entity, query = tratar_intencao(context.message.text)
    if intencao == SAUDACAO:
        tratar_saudacao(bot, context)
        return IDLE
    elif intencao == CONSULTAR_CHAMADO:
        response = tratar_consultar_chamado(bot, context)
        return CONSULTAR_CHAMADO_STATE
    elif intencao == ABRIR_CHAMADO:
        response = tratar_abrir_chamado(bot, context)
        return CRIAR_CHAMADO
    else:
        response = tratar_nao_reconhecimento(bot, context)
    return response


def tratar_intencao(text):
    print("to no luis")
    luis_conn = LUISConnector(model_file=None)
    intent = luis_conn._process(text)
    intencao = intent.intents[0].intent
    entity = ''
    if len(intent.entities) > 0:
        entity = intent.entities[-1].resolution['value']
    print(intencao)
    return intencao, entity, intent.query


def tratar_retorno(text):
    resp = 'O chamado nº: "' + str(text.get('issue').get('id')) + '"' + \
        ' está com status: "' + str(text.get('issue').get('status').get('name')) \
        + '" e possui a descrição: "' + \
        str(text.get('issue').get('subject')) + '".\n'
    return resp


def tratar_saudacao(update, context):
    print("Tratando saudacao")
    response = "Olá {}, sou um bot de demonstração!!\n".format(context.message.from_user.first_name)
    response += "Estou aqui para criar e consultar chamados.\n"
    response += "\n1- Para consultar chamados, utilize a sintaxe:"
    response += "\n       'você poderia consultar o chamado 1'"
    response += "\n\n2- Para cadastrar chamados, utilize a sintaxe:"
    response += "\n       'cadastrar um chamado para: perda de celular'"
    print(response)
    context.message.reply_text(response)
    return IDLE

# AQUI
def tratar_consultar_chamado(bot, context):
    response = "Olá {}, qual chamado gostaria de consultar?\n\n".format(
        context.message.from_user.first_name)
    context.message.reply_text(response)
    return

def consultar_chamado(bot, context):
    user = context.message.from_user
    chamado = context.message.text
    
    red = Redmine()
    response = 'Não foi possível consultar seu chamado.'
    if chamado is not '':
        resp = red.execute_get(chamado)
        response = "Olá {}, abaixo os dados do seu chamado:\n\n".format(
            user.first_name)
        response += tratar_retorno(resp)
    context.message.reply_text(response)
    return IDLE


def tratar_abrir_chamado(bot, context):
    context.message.reply_text("Okay, qual será a descrição do chamado?")
    return

def abrir_chamado(bot, context):
    red = Redmine()
    response = context.message.text
    if len(response) > 1:
        resp = red.execute_post(context.message.text)
        response = "Chamado {} aberto com sucesso\n".format(
            resp.get('issue').get('id'))
    else:
        response = "Não foi possível criar o seu chamado." 
    context.message.reply_text(response)
    
    return IDLE


def cancel(update, context):
    user = context.message.from_user
    context.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END


def tratar_nao_reconhecimento(first_name):
    response = "Olá {}, não entendi o que você disse. Poderia repetir?\n" \
        .format(first_name)
    return response


def main():
    # Create the updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("814759196:AAGo4IT2z_ShbXO6avRMIxliK_h9t8rZUVY")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', tratar_saudacao)],
        # SAUDACAO, CRIAR_CHAMADO, CHAMADO_CRIADO, CONSULTAR_CHAMADO, CHAMADO_CONSULTADO = range(5)
        states={
            IDLE: [MessageHandler(Filters.text, control_flux)],
            CONSULTAR_CHAMADO_STATE: [MessageHandler(Filters.text,consultar_chamado)],
            CRIAR_CHAMADO: [MessageHandler(Filters.text,abrir_chamado)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    print("Up")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


'''
if __name__ == '__main__':
    # a = tratar_intencao('Oi')
    # print(a)
    publish_telegram_msg({'resource': '/teleg-bot-demo', 
        'path': '/teleg-bot-demo', 'httpMethod': 'POST', 
        'headers': {'Accept-Encoding': 'gzip, deflate', 
        'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 
        'true', 'CloudFront-Is-Mobile-Viewer': 'false', 
        'CloudFront-Is-SmartTV-Viewer': 'false', 
        'CloudFront-Is-Tablet-Viewer': 'false', 
        'CloudFront-Viewer-Country': 'GB', 'Content-Type': 
        'application/json', v
        'Host': '29hthkrsx0.execute-api.us-east-2.amazonaws.com', 
        'Via': '1.1 5fe8343a80de49928fae39084e131a25.cloudfront.net (CloudFront)', 
        'X-Amz-Cf-Id': 'IN69kYU2zS1Xi_zGUdgEdmvLH1Sg8ah9hwj9bPA-yRDEU8bkZmUocw==', 
        'X-Amzn-Trace-Id': 'Root=1-5cb6fc3a-2248bb2cd6151a58c47a5f36', 
        'X-Forwarded-For': '149.154.167.229, 54.240.156.99', 
        'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 
        'multiValueHeaders': {'Accept-Encoding': ['gzip, deflate'], 
        'CloudFront-Forwarded-Proto': ['https'], 
        'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': 
        ['false'], 'CloudFront-Is-SmartTV-Viewer': ['false'], 
        'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-Country': ['GB'], 
        'Content-Type': ['application/json'], 
        'Host': ['29hthkrsx0.execute-api.us-east-2.amazonaws.com'], 
        'Via': ['1.1 5fe8343a80de49928fae39084e131a25.cloudfront.net (CloudFront)'], 
        'X-Amz-Cf-Id': ['IN69kYU2zS1Xi_zGUdgEdmvLH1Sg8ah9hwj9bPA-yRDEU8bkZmUocw=='], 
        'X-Amzn-Trace-Id': ['Root=1-5cb6fc3a-2248bb2cd6151a58c47a5f36'], 
        'X-Forwarded-For': ['149.154.167.229, 54.240.156.99'], 
        'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 
        'queryStringParameters': None, 'multiValueQueryStringParameters': 
        None, 'pathParameters': None, 'stageVariables': None, 
        'requestContext': {'resourceId': 'ty7i49', 'resourcePath': 
        '/teleg-bot-demo', 'httpMethod': 'POST', 
        'extendedRequestId': 'YRxZMHJACYcF3LQ=', 
        'requestTime': '17/Apr/2019:10:13:14 +0000', 
        'path': '/dev/teleg-bot-demo', 'accountId': '175187370354', 
        'protocol': 'HTTP/1.1', 'stage': 'dev', 'domainPrefix': '29hthkrsx0', 
        'requestTimeEpoch': 1555495994851, 'requestId': 
        '69bb33af-60f9-11e9-a015-1d41eb305e2f', 'identity': 
        {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': 
        None, 'caller': None, 'sourceIp': '149.154.167.229', 
        'accessKey': None, 'cognitoAuthenticationType': None, 
        'cognitoAuthenticationProvider': None, 'userArn': None, 
        'userAgent': None, 'user': None}, 'domainName': 
        '29hthkrsx0.execute-api.us-east-2.amazonaws.com', 'apiId': '29hthkrsx0'}, 
        'body': '{"update_id":241554614,\n"message":{"message_id":131,"from":{"id":68330001,"is_bot":false,"first_name":"Evandro","last_name":"Franco","username":"evandrofranco","language_code":"pt-br"},"chat":{"id":68330001,"first_name":"Evandro","last_name":"Franco","username":"evandrofranco","type":"private"},"date":1555495019,"text":"você poderia consultar o chamado 1"}}', 'isBase64Encoded': False}, '')
'''


if __name__ == '__main__':
    print("Starting")
    main()
