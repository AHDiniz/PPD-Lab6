# PPD-Lab6

Trabalho de Processamento Paralelo e Distribuído simulando uma blockchain.

## Instalação

Para rodar corretamente este projeto, instale as dependencias python contidas no arquivo [requirements.txt](./requirements.txt). Uma forma rápida de realizar essas instalações é rodar, caso esteja usando python, o comando:

`$ pip install -r ./requirements.txt`

ou, caso esteja usando python3, o comando:

`$ pip3 install -r ./requirements.txt`

Este projeto requer ainda a instalação do [RabbitMQ&trade;](https://www.rabbitmq.com/).

## Rodando

Para rodar este programa, primeiro esteja certo de ter o [RabbitMQ&trade;](https://www.rabbitmq.com/) instalado, para instalar é possível utilizar o script [inst.sh](./inst.sh) disponibilizado. Após isto, rode o cliente, caso esteja usando python, com o comando:

`$ python miner/main.py <number_of_nodes>`

ou, caso esteja usando python3, o comando:

`$ python3 miner/main.py <number_of_nodes>`


## Detalhes de Implementação

## RSA Keys
Para geração das chaves, utilizamos o script `generate.sh`, então recuperamos a chave e salvamos em memória. Cada vez que a aplicação é iniciada, um novo par de chaves é gerado.

## Subscrever e Publicar ao mesmo tempo
Dado que o pika não é thread safe, geramos uma conexão para cada conexão necessária.

### Consumidor Principal
Geramos uma conexão principal de consumo de todas as mensagens. Nela geramos filas específicas para publicarmos nos exchanges definidos na especificação, utilizando do NodeId do cliente mais um número random de 32 bits.

### Publicador da thread principal 
Geramos um publicador para envio das mensagens:

- InitMsg
- PubKeyMsg
- ElectionMsg
- ChallengeMsg

Essas mensagens não são enviadas pelas outras threads então foi possível manter-las na main


#### Publicador das threads de mineração
Para cada uma das threads de mineração do cliente, geramos uma nova conexão para podermos publicar a mensagem de solução.
Essas threads rodam enquanto o estado do sistema estiver em Running e são recriadas todas as vezes que um novo desafio é recebido.

## Sobre o [RabbitMQ&trade;](https://www.rabbitmq.com/)

> With tens of thousands of users, RabbitMQ is one of the most popular open source message brokers. From T-Mobile to Runtastic, RabbitMQ is used worldwide at small startups and large enterprises.

> RabbitMQ is lightweight and easy to deploy on premises and in the cloud. It supports multiple messaging protocols. RabbitMQ can be deployed in distributed and federated configurations to meet high-scale, high-availability requirements.

> RabbitMQ runs on many operating systems and cloud environments, and provides a wide range of developer tools for most popular languages.

Texto retirado do site https://www.rabbitmq.com/. Acessado no dia 14/07/2022.
