# AWS Framework

Este projeto Demo para fazer um Bot do Telegram, hospedado na AWS (lambda) 

# Pré-Requisitos

Possuir NodeJS e NPM Instalados

Instalar o framework:
    
    npm install -g serverless

    sls plugin install -n serverless-python-requirements

Rodar os pre-requisitos do Python:

    pip install -r requirements.txt

## Criação / Remoção AWS

Para criar a stack na AWS, basta executar o comando abaixo na raiz do projeto

    sls deploy

Para remover a stack:

    sls remove