import socket
import threading
import mysql.connector
import bcrypt
import datetime
from GoogleNews import GoogleNews
import pandas as pd
from datetime import date
import smtplib

################################## - // - ######################################
def conectar_banco():

    conexao = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "project_webScraping"
    )
    return conexao
# -- #

def envia_Email(emai, news_text):
    import email.message
    msg = email.message.Message()
    msg['From'] = 'alissonmarqueshm30@gmail.com'
    msg['Subject'] = 'TRABALHO DE PYTHON'
    msg['To'] = emai

    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(news_text)

    password = 'thrcsphizixlgcup'
    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], msg['To'], msg.as_string().encode('utf-8'))
    print('Passei do enviar')
# -- #

def enviaEmails(noticias, email):

    if noticias:

        news_text = ""
        for news in noticias:
            title = news["title"]
            link = news["link"]

            #para remover uma parte do html que nao eh necessario para abertura do link
            link_parts = link.split('&')
            clean_link = link_parts[0]

            news_text += f'Título: {title}<br>'
            news_text += f'Link: <a href="{clean_link}">{clean_link}</a><br><br>'

        envia_Email(email, news_text)
    else:
        
        print('Sem notícias')
# -- #

def buscar_noticiasEmail():

    hoje = date.today()
    email = ""
    
    conexao = conectar_banco()
    cursor = conexao.cursor()

    query = 'select * from email_programado;'
    cursor.execute(query, [])
    programacoesDeEnvio = cursor.fetchall()
    essesJaForam = []
    for i in programacoesDeEnvio:

        if (i[4] not in essesJaForam):
            query = 'select email from Usuarios where id = %s;'
            cursor.execute(query, [i[4]])
            emailParaEnviar = cursor.fetchone()

            essesJaForam.append(i[4])
            quantInfo = []
            assunto = []
            secao = []
            for a in programacoesDeEnvio:

                if a[4] == i[4] and (a[1] == hoje or a[1] == 7):

                    secao.append(a[5])
                    quantInfo.append(a[2])
                    assunto.append(a[3])

            matching_news = []
            for a in range(len(quantInfo)):

                googlenews = GoogleNews(lang='pt', region='BR', period='7d')

                try:
                    # faz a raspagem com a lib
                    googlenews.search(assunto[a])

                    # pega os resultados
                    result = googlenews.result()

                    # faz a conversao para DataFrame usando pandas
                    df = pd.DataFrame(result)

                    # faz a filtragem para a quantidade desejada de notihcias
                    df = df.head(int(quantInfo[a]))

                    for i in range(min(int(quantInfo[a]), len(df))):
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

            if matching_news != []:
                print(emailParaEnviar[0])
                enviaEmails(matching_news, emailParaEnviar[0])
                print('Emails enviados com sucesso!')
################################# - // - #######################################
class ClientThread(threading.Thread):

    '''
    Esta classe representa um cliente conectado ao servidor

    ...
    Attributes
    ----------
    conexao: socket.socket()
        responsável pela conexão do cliente com o servidor
    clienteAddress: socket.socket()
        responsável pela identificação do cliente
    startEnd: threading.Event()
        responsável por especificar se o cliente ainda está conectado

    METHODS
    -------
    run()
        Responsável por especificar o ciclo do cliente dentro do servidor
    verificaLogin(email, senha)
        Reponsável por verificar se o cliente está cadastrado na base de dados
    cadastrar(first_name, second_name, email, senha, data_nascimento)
        Responsável por cadastrar um cliente na base de dados
    buscarNoticias(keyword, qntd_tela, section)
        Responsável por buscar notícias com base em palavras-chaves dadas pelo cliente
    exibir_noticias(noticias)
        Responsável por enviar as notícias para o cliente
    programarNoticias(keyword, quantidade, frequencia, section, email)
        Responsável por cadastrar na base de dados as programações de envio por email
    '''
    def __init__(self, conexao, clienteAddress):

        '''
        Parameters
        ----------
        conexao: socket.socket()
            responsável pela conexão do cliente com o servidor
        clienteAddress: socket.socket()
            responsável pela identificação do cliente
        startEnd: threading.Event()
            responsável por especificar se o cliente ainda está conectado
        '''
        super().__init__()
        self.conexao = conexao
        self.clienteAddress = clienteAddress
        self.startEnd = threading.Event()

    def run(self):

        '''
        Responsável pelo funcionamento das opções do cliente

        Parameters
        ----------
        
        Returns
        -------

        Raises
        ------
        '''
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

        '''
        Reponsável por verificar se o cliente está cadastrado na base de dados

        Parameters
        ----------
        email: str
            email informado pelo usuário conectado
        senha: str
            senha informada pelo usuário conectado
            
        Returns
        -------
        retorno: str
            Reponsável por identificar a confirmação do login
            
        Raises
        ------
        '''
        # senha_hash = senha.encode('utf-8')
        conexao = conectar_banco()
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
        conexao = conectar_banco()

        '''
        Responsável por cadastrar um cliente na base de dados
        
        Parameters
        ----------
        first_name: str
            Primeiro nome do cliente a ser cadastrado na base de dados
        second_name: str
            Segundo nome do cliente a ser cadastrado na base de dados
        email: str
            Email do cliente a ser cadastrado na base de dados
        senha: str
            Senha do cliente a ser cadastrado na base de dados
        data_nascimento: str
            Data de nascimento do cliente a ser cadastrado na base de dados
            
        Returns
        -------
            Retorno responsável por identificar o êxito da operação
            
        Raises
        ------
        '''
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

        '''
        Responsável por buscar notícias com base em palavras-chaves dadas pelo cliente

        Parameters
        ----------
        keyword: str
            Palavra chave da pesquisa web
        qntdtela: int
            Quantidade de notícias a serem retornadas
        section: str
            Seção em que a palavra chave será buscada
        
        Returns
        -------

        Raises
        ------
        '''
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

                # condicao para verificar se a palavra-chave estah no tihtulo
                if keyword.lower() in title.lower():
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
        '''
        Responsável por enviar as notícias para o cliente

        Parameters
        ----------
        noticias: []
            Notícias a serem enviadas para o usuário
        
        Returns
        -------

        Raises
        ------
        '''
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

        '''
        Responsável por cadastrar na base de dados as programações de envio por email
     
        Parameters
        ----------
        keyword: str
            Palavra chave da pesquisa web
        quantidade: str
            Quantidade de notícias a serem retornadas
        frequencia: str
            Dia/dias da semana que será enviada as notícias
        section: str
            Seção em que a palavra chave será buscada
        email: str
            Email do usuário conectado
            
        Returns
        -------

        Raises
        ------
        '''
        conexao = conectar_banco()
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

buscar_noticiasEmail()

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
