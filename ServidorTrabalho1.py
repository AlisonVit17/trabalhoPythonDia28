import socket
import threading
import mysql.connector
import bcrypt
import datetime
import requests
from bs4 import BeautifulSoup

class ClientThread(threading.Thread):

    def __init__(self, conexao, clienteAddress):

        super().__init__()
        self.conexao = conexao
        self.clienteAddress = clienteAddress
        self.startEnd = threading.Event()

    def run(self):

        try:
            while not self.startEnd.is_set():
                opcao = self.conexao.recv(1024)

                print(f"Opção: {opcao.decode()}")

                if opcao.decode() == '1':
                    recebido = self.conexao.recv(1024).decode().split(',')

                    if recebido:
                        email = recebido[0]
                        senha = recebido[1]

                        enviar = self.verificaLogin(email, senha)

                        self.conexao.send(enviar.encode())

                    else:
                        print("Erro ao receber dados do cliente")
                        self.conexao.send('-1'.encode())
                elif opcao.decode() == '2':

                    data = self.conexao.recv(1024).decode().split(',')

                    if data:
                        first_name = data[0]
                        second_name = data[1]
                        email = data[2]
                        senhaa = data[3]
                        data_nascimento = data[4]

                        self.cadastrar(first_name, second_name, email, senhaa, data_nascimento)
                        self.conexao.send('1'.encode())
                    else:
                        self.conexao.send('-1'.encode())

                elif opcao.decode() == '3':
                    data = self.conexao.recv(1024).decode().split(',')
                    keyword = data[0]
                    qntd_tela = int(data[1])
                    section = data[2]
                    print(f"Keyword: {keyword} - Quantidade de Notícias: {qntd_tela} - Seção: {section}")
                    self.buscarNoticias(keyword, qntd_tela, section)
                elif opcao.decode() == '4':
                    data = self.conexao.recv(1024).decode().split(',')
                    keyword = data[0]
                    qntd_tela = int(data[1])
                    section = data[2]
                    print(f"Keyword: {keyword} - Quantidade de Notícias: {qntd_tela} - Seção: {section}")
                    self.programarNoticias(keyword, qntd_tela, section)
                elif opcao.decode() == '-1':
                    break
                elif opcao.decode() == '0':
                    pass

        except Exception as e:
            print(f"Erro ao receber dados do cliente: {e}")
        finally:
            print('Disconnected')
            self.conexao.close()
            self.startEnd.set()

    def verificaLogin(self, email, senha):

        # senha_hash = senha.encode('utf-8')
        conexao = self.conectar_banco()
        cursor = conexao.cursor()

        try:
            query = "SELECT * FROM usuarios WHERE email_ou_telefone = %s"
            cursor.execute(query, (email,))
            usuario = cursor.fetchone()


            if usuario:
                hash_guardado = usuario[4].encode('utf-8')
                if bcrypt.checkpw(senha.encode('utf-8'), hash_guardado):
                    return '1'
                else:

                    print("Senha incorreta")
                    return '-1'
            else:
                print("usuario nao encontrado")
        except Exception as exc:
            print(f"Erro ao verificar login: {exc}")
            return '-1'

        finally:
            cursor.close()
            conexao.close()

    def cadastrar(self, first_name, second_name, email, senha, data_nascimento):
        conexao = self.conectar_banco()

        try:
            cursor = conexao.cursor()

            query = "SELECT * FROM usuarios WHERE email_ou_telefone = %s;"
            cursor.execute(query, (email,))
            usuario = cursor.fetchone()

            if usuario:
                self.conexao.send('-2'.encode())
                cursor.close()
                conexao.close()
                return '-2'

            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

            if conexao:
                cursor = conexao.cursor()
                data_nasci = datetime.datetime.strptime(data_nascimento, '%d/%m/%Y').date()

                query = "INSERT INTO usuarios (primeiro_nome, segundo_nome, email_ou_telefone, senha, data_nascimento) VALUES (%s, %s, %s, %s, %s);"
                cursor.execute(query, (first_name, second_name, email, senha_hash, data_nasci))
                conexao.commit()


                cursor.close()
                conexao.close()
                return '1'

            else:
                print("Erro ao conectar ao banco de dados")
                return '-1'
        except Exception as e:
            print(f"Erro ao cadastrar usuário: {e}")
            return '-1'


    def buscarNoticias(self, keyword, qntd_tela, section):


        url = f'https://news.google.com/search?q={keyword}&hl=en-US&gl=US&ceid=US:en&section={section}'
        print("enttrei na busca de noticias")
        response = requests.get(url)

        if response.status_code == 200:
            print("passei do codigo de 200")
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('h3', class_='ipQwMb')

            matching_news = []

            for i, article in enumerate(articles):
                if i >= qntd_tela:
                    break
                title = article.text
                link = 'https://news.google.com' + article.a['href']
                print("cheguei antes do retorno")
                if keyword.lower() in title.lower():
                    matching_news.append({'title': title, 'link': link})
                    return "1"

                else:
                    return "-2"
        else:
            return "-1"

    def programarNoticias(self, keyword, qntd_tela, section):

            url = f'https://news.google.com/search?q={keyword}&hl=en-US&gl=US&ceid=US:en&section={section}'
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all('h3', class_='ipQwMb')

                matching_news = []

                for i, article in enumerate(articles):
                    if i >= qntd_tela:
                        break
                    title = article.text
                    link = 'https://news.google.com' + article.a['href']

                    if keyword.lower() in title.lower():
                        matching_news.append({'title': title, 'link': link})

                if len(matching_news) > 0:
                    conexao = self.conectar_banco()
                    cursor = conexao.cursor()

                    query = "SELECT * FROM usuarios;"
                    cursor.execute(query)
                    usuarios = cursor.fetchall()

                    for usuario in usuarios:
                        email = usuario[3]
                        senha = usuario[4]
                        self.enviarEmail(email, senha, matching_news)

                    cursor.close()
                    conexao.close()

                else:
                    print("Nenhuma notícia encontrada")
            else:
                print("Erro ao conectar ao Google News")

    def enviarEmail(self, email, senha, noticias):
        print("entrou no enviar email")
        pass

    def conectar_banco(self):

        conexao = mysql.connector.connect(
            host= "localhost",
            user= "root",
            password= "031012Gui@",
            database= "project_webScraping"
        )
        return conexao


host = ''

port = 9005

addr = (host, port)

serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv_socket.bind(addr)
serv_socket.listen(30)


while(True):

    try:
        print('aguardando conexao...')
        con, cliente = serv_socket.accept()
        print('conectado')
        cliente = ClientThread(con, cliente)
        cliente.start()
        #enviar = input('digite uma mensagem para enviar ao cliente: ')
        #con.send(enviar.encode()) #enviar uma mensagem para o cliente
    except Exception as e:
        print(f"Erro ao aceitar conexão: {e}")
