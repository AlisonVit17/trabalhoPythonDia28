import socket
import threading
import mysql.connector
import bcrypt
import datetime
from GoogleNews import GoogleNews
import pandas as pd


class ClientThread(threading.Thread):

    def __init__(self, conexao, clienteAddress):

        super().__init__()
        self.conexao = conexao
        self.clienteAddress = clienteAddress
        self.startEnd = threading.Event()

    def run(self):

        try:
            while not self.startEnd.is_set():
                print('Aguardando nova opção')
                opcao = self.conexao.recv(1024)

                print(f"Opção: {opcao.decode()}")

                if opcao.decode() == '1':
                    recebido = self.conexao.recv(1024).decode().split(',')#

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
                    
                    data = self.conexao.recv(1024).decode().split(',')#1
                    keyword = data[0]
                    qntd_tela = int(data[1])
                    section = data[2]
                    print(f"Keyword: {keyword} - Quantidade de Notícias: {qntd_tela} - Seção: {section}")
                    self.buscarNoticias(keyword, qntd_tela, section)


                elif opcao.decode() == '4':

                    data = self.conexao.recv(1024).decode().split(',')#1
                    quantidade = data[0]
                    keyword = data[1]
                    frequencia = data[2]
                    section = data[3]
                    email = data[4]
                    self.programarNoticias(keyword, quantidade, frequencia, section, email)
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
        retorno = ''
        try:
            query = "SELECT * FROM usuarios WHERE email = %s"
            cursor.execute(query, [email])
            usuario = cursor.fetchone()


            if usuario:

                hash_guardado = usuario[4].encode('utf-8')
                if bcrypt.checkpw(senha.encode('utf-8'), hash_guardado):
                    retorno = '1'
                else:

                    print("Senha incorreta")
                    retorno = '-1'
            else:
                
                print("usuario nao encontrado")
                retorno = '-1'
        except Exception as exc:
            print(f"Erro ao verificar login: {exc}")
            retorno = '-1'

        finally:
            cursor.close()
            conexao.close()

        return retorno

    def cadastrar(self, first_name, second_name, email, senha, data_nascimento):
        conexao = self.conectar_banco()

        try:
            cursor = conexao.cursor()

            query = "SELECT * FROM usuarios WHERE email = %s;"
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

                query = "INSERT INTO usuarios (first_name, second_name, email, senha, data_nascimento) VALUES (%s, %s, %s, %s, %s);"
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
        # opcional - com a lib do googleNews, podemos acrescentar o periodo para nao pegar noticias tao antigas
        # acrescentar internamente, por nos mesmo , sem o usuario
        googlenews = GoogleNews(lang='pt', region='BR', period='7d')

        try:
            # faz a raspagem com a lib
            googlenews.search(keyword)

            # pega os resultados
            result = googlenews.result()

            # faz a conversao para DataFrame usando pandas
            df = pd.DataFrame(result)

            # faz a filtragem para a quantidade desejada de notihcias
            df = df.head(int(qntd_tela))

            matching_news = []
            for i in range(min(int(qntd_tela), len(df))):
                title = df['title'][i]
                link = df['link'][i]
                print(link)

                # para ver se o link é uma URL válida
                if not link.startswith('http'):
                    link = 'https://news.google.com' + link

                # para remover caracteres especiais do link
                link = link.encode('utf-8').decode('ascii', 'ignore')

                newss = {'title': title, 'link': link}
                matching_news.append(newss)

            retorno = "1"
        except Exception as e:
            retorno = "-1"
            msg = f"Erro ao buscar notícias: {e}"
            print(msg)

        self.conexao.send(retorno.encode())  # 2
        if (self.conexao.recv(1024).decode()):  # 3
            if retorno != "1":
                self.conexao.send(msg.encode())
            else:
                self.exibir_noticias(matching_news)

    def exibir_noticias(self, noticias):

        if noticias:
            news_text = ""
            for news in noticias:
                title = news["title"]
                link = news["link"]

                # para remover uma parte do html que nao eh necessario para abertura do link
                link_parts = link.split('&')
                clean_link = link_parts[0]

                news_text += f'Título: {title}<br>'
                news_text += f'Link: <a href="{clean_link}">{clean_link}</a><br><br>'

            self.conexao.send(news_text.encode())
        else:
            self.conexao.send('Sem notícias'.encode())
            print('Sem notícias')


    # def buscarNoticias(self, keyword, qntd_tela, section):
    #
    #     url = f'https://news.google.com/search?q={keyword}&hl=en-US&gl=US&ceid=US:en&section={section}'
    #     response = requests.get(url)
    #     retorno = ""
    #     msg = ""
    #
    #     try:
    #         if response.status_code == 200:
    #
    #             soup = BeautifulSoup(response.content, 'html.parser')
    #             articles = soup.find_all('h3', class_='ipQwMb')
    #             matching_news = []
    #
    #             for i, article in enumerate(articles):
    #                 if i >= qntd_tela:
    #
    #                     break
    #
    #                 title = article.text
    #                 link = 'https://news.google.com' + article.a['href']
    #                 print("cheguei antes do retorno")
    #                 if keyword.lower() in title.lower():
    #                     matching_news.append({'title': title, 'link': link})
    #
    #
    #             retorno = "1"
    #
    #         else:
    #             retorno = "-1"
    #             msg = "Não encontrado :("
    #
    #         self.conexao.send(retorno.encode())#2
    #         if(self.conexao.recv(1024).decode()):#3
    #             if retorno != "1":
    #
    #                 self.conexao.send(msg.encode())
    #             else:
    #
    #                 self.exibir_noticias(matching_news)
    #     except Exception as e:
    #         print(f"Erro ao buscar notícias: {e}")
    #
    #
    #
    # def exibir_noticias(self, noticias): #noticias é uma lista, talvez vazia...
    #
    #     if noticias:
    #
    #         news_text = ""
    #         for news in noticias:
    #
    #             news_text += f'Título: {news["title"]}<br>'
    #             news_text += f'Link: <a href="{news["link"]}">{news["link"]}</a><br><br>'
    #
    #         self.conexao.send(news_text.encode())
    #     else:
    #
    #         self.conexao.send('Sem notícias'.encode())
    #         print('Sem notícias')

    def programarNoticias(self, keyword, quantidade, frequencia, section, email):

            conexao = self.conectar_banco()
            cursor = conexao.cursor()
            cursor.execute('select id from usuarios where email = %s;', [email])
            id_user = cursor.fetchone()

            if frequencia == 'Domingo':

                frequencia = '0'
            elif frequencia == 'Segunda-feira':

                frequencia = '1'
            elif frequencia == 'Terça-feira':

                frequencia = '2'
            elif frequencia == 'Quarta-feira':

                frequencia = '3'
            elif frequencia == 'Quinta-feira':

                frequencia = '4'
            elif frequencia == 'Sexta-feira':

                frequencia = '5'
            elif frequencia == 'Sábado':

                frequencia = '6'
            else:

                frequencia = '7'
                
            if id_user:

                query = 'insert into email_programado(id_programado, dia, quant_info, noticias, id_users, section) values(default, %s, %s, %s, %s, %s);'
                cursor.execute(query, [frequencia, quantidade, keyword, id_user[0], section])
                self.conexao.send('1'.encode())#2
            else:

                self.conexao.send('-1'.encode())#2
                
    def enviarEmail(self, email, senha, noticias):
        print("entrou no enviar email")
        pass

    def conectar_banco(self):

        conexao = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "",
            database = "project_webScraping"
        )
        return conexao


host = ''

port = 9009

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
