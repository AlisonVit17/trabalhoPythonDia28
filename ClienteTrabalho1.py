import socket

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget
from PyQt5.uic import loadUi
from qdarkstyle import load_stylesheet_pyqt5


class LoginPage(QMainWindow):
    _quantEmailsComProgramacoes = 0

    '''
    Esta classe representa um cliente que acessa o servidor

    ...

    Attributes
    ----------
    client_socket: socket.socket()
        responsável pela conexão do cliente com o servidor
    setWindowTitle: setWindowTitle()
        Responsável pelo nome da página
    setGeometry: setGeometry()
        Responsável pelo tamanho da janela
    stacked_widget: QStackedWidget()
        Responsável pela mudança de janelas
    setCentralWidget setCentralWidget()
        Widget central da página, nele são mostradas as janelas
    mainPage: QtWidget()
        Primeira tela que será visualizada pelo cliente, nela são mostradas as
        opções de login e de cadastro
    cadastroPage: QtWidget()
        Tela responsável pela captura dos dados de cadastro do cliente
    tela_02: QtWidget()
        Tela responsável pela captura de informações para a realização de uma
        pesquisa, ou mesmo para a opção de programar envio
    programarEnvio: QtWidget()
        Tela responsável pela programação de envio por email
    about_us: QtWidget()
        Tela de aviso, responsável pela saída da aplcação
    confirmaSaida: QtWidget()
        Tela responsável pela confirmação de logout

    METHODS
    -------
    setup_ui()
        Responsável pelas configurações das telas, bem como suas funcionalidades
    show()
        Responsavel por mostrar a tela dos arquivos .ui
    mostrar_cadastro()
        Conexão responsável por mostrar a tela de cadastro
    voltar_main_page()
        Conexão responsável por mostrar a tela main do cliente
    toggle_theme()
        Conexão responsável por chamar o método de alteração da cor de fundo
        da aplicação
    apply_theme(theme_name: str)
        Conexão responsável por alterar a cor de fundo da aplicação
    callback_login()
        Conexão responsável pelo login do usuário
    callback_cadastro()
        Conexão responsável pelo cadastro do usuário
    buscar_noticiasTela()
        Conexão responsável por mostrar para o cliente as notícias retornadas
    programaEnvio()
        Conexão responsável pela programação de envio por email
    programarEnvioTela()
        Conexão responsável por chamar a tela de programar envios para email
    callback_exit()
        Conexão responsável por sair da aplicação
    about_uss()
        Conexão responsável pela chamada de uma tela para confirmação da saída
        da aplicação
    confirmarSaida()
        Conexão responsável pela chamada da tela de confirmação de logout
    telaDeBusca()
        Conexão responsável pela chamada da tela de pesquisas
    '''
    def __init__(self, client_socket):

        '''
        Parameters
        ----------
        client_socket: socket.socket()
            responsável pela conexão do cliente com o servidor
        setWindowTitle: setWindowTitle()
            Responsável pelo nome da página
        setGeometry: setGeometry()
            Responsável pelo tamanho da janela
        stacked_widget: QStackedWidget()
            Responsável pela mudança de janelas
        setCentralWidget setCentralWidget()
            Widget central da página, nele são mostradas as janelas
        mainPage: QtWidget()
            Primeira tela que será visualizada pelo cliente, nela são mostradas as
            opções de login e de cadastro
        cadastroPage: QtWidget()
            Tela responsável pela captura dos dados de cadastro do cliente
        tela_02: QtWidget()
            Tela responsável pela captura de informações para a realização de uma
            pesquisa, ou mesmo para a opção de programar envio
        programarEnvio: QtWidget()
            Tela responsável pela programação de envio por email
        about_us: QtWidget()
            Tela de aviso, responsável pela saída da aplcação
        confirmaSaida: QtWidget()
            Tela responsável pela confirmação de logout
        '''
        
        super().__init__()
        self.client_socket = client_socket
        self.setWindowTitle('Cadastro de Usuário')
        self.setGeometry(500, 200, 750, 600)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.mainPage = loadUi('files_ui/mainPage.ui')
        self.cadastroPage = loadUi('files_ui/register.ui')
        self.tela_02 = loadUi('files_ui/tela_02.ui')
        self.programarEnvio = loadUi('files_ui/programarTela.ui')
        self.about_us = loadUi('files_ui/about_us.ui')
        self.confirmaSaida = loadUi('files_ui/confirmaSaida.ui')
        self.setup_ui()
        self.show()

        self.mainPage.light_dark.currentIndexChanged.connect(self.toggle_theme)
        self.apply_theme("Light")

    def setup_ui(self):

        '''
        Responsável pelas configurações das telas, bem como suas funcionalidades

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''
        self.stacked_widget.addWidget(self.mainPage)
        self.stacked_widget.addWidget(self.cadastroPage)
        self.stacked_widget.addWidget(self.tela_02)
        self.stacked_widget.addWidget(self.about_us)
        self.stacked_widget.addWidget(self.confirmaSaida)
        self.stacked_widget.addWidget(self.programarEnvio)

        self.mainPage.createAccount_button.clicked.connect(self.mostrar_cadastro)
        self.cadastroPage.voltar_button.clicked.connect(self.voltar_main_page)
        self.mainPage.login_button.clicked.connect(self.callback_login)
        self.cadastroPage.cadastrar_button.clicked.connect(self.callback_cadastro)
        self.mainPage.exit_button.clicked.connect(self.callback_exit)
        self.mainPage.about_us.clicked.connect(self.about_uss_funcao)
        self.tela_02.logout_btn.clicked.connect(self.confirmarSaidaFuncao)
        self.tela_02.search_btn.clicked.connect(self.buscar_noticiasTela)
        self.tela_02.envioProgramado.clicked.connect(self.programarEnvioTela)
        self.programarEnvio.voltarMostrarTela.clicked.connect(self.telaDeBusca)
        self.programarEnvio.programar.clicked.connect(self.programaEnvioEmail)
        self.about_us.back_butt.clicked.connect(self.voltar_main_page)
        self.confirmaSaida.logout.clicked.connect(self.voltar_main_page)
        self.confirmaSaida.cancel.clicked.connect(self.telaDeBusca)

        self.mainPage.email_or_phone.setPlaceholderText('Email')
        self.mainPage.password.setPlaceholderText('Password')
        self.cadastroPage.first_name.setPlaceholderText('First Name')
        self.cadastroPage.second_name.setPlaceholderText('Last Name')
        self.cadastroPage.email_or_phone.setPlaceholderText('Email')
        self.cadastroPage.password.setPlaceholderText('Password')
        self.cadastroPage.confirm_password.setPlaceholderText('Confirm Password')
        self.tela_02.key_word.setPlaceholderText('Enter with the key')

        self.mainPage.light_dark.addItems(["Light", "Dark"])
        self.tela_02.qntd_tela.addItems(["1", "2", "3", "4", "5"])
        self.tela_02.filter_tela.addItems(["Home", "World", "Local", "Business", "Technology"])

    def mostrar_cadastro(self):

        '''
        Método responsável por mostrar a tela de cadastro

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''
        self.stacked_widget.setCurrentIndex(1)

    def voltar_main_page(self):

        '''
        Conexão responsável por mostrar a tela main do cliente

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''        
        self.stacked_widget.setCurrentIndex(0)
        self.mainPage.password.clear()
        self.mainPage.email_or_phone.clear()

    def toggle_theme(self):
        '''
        Conexão responsável por chamar o método de alteração da cor de fundo
        da aplicação

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''
        selected_theme = self.mainPage.light_dark.currentText()
        self.apply_theme(selected_theme)

    def apply_theme(self, theme_name):

        '''
        Conexão responsável por alterar a cor de fundo da aplicação

        Parameters
        ----------
        theme_name: str
            String com o nome do novo plano de fundo

        Returns
        -------

        Raises
        ------        
        '''
        if theme_name == "Dark":
            self.setStyleSheet(load_stylesheet_pyqt5())
        else:
            self.setStyleSheet("")

    def callback_login(self):

        '''
        Conexão responsável pelo login do usuário

        Parameters
        ----------
  
        Returns
        -------

        Raises
        ------        
        '''
        opcao = '1'
        self.client_socket.send(opcao.encode())

        email = self.mainPage.email_or_phone.text()
        senha = self.mainPage.password.text()

        if email == '' or senha == '':
            self.client_socket.send(''.encode())
            senha = ''
            email = ''

        string = f"{email},{senha}"

        try:
            self.client_socket.send(string.encode())
            retorno = self.client_socket.recv(1024).decode()#

            if retorno == '1':
                
                self.stacked_widget.setCurrentIndex(2)
                QMessageBox.warning(self, 'Login', 'Login realizado com sucesso')
            elif retorno == '-1':

                QMessageBox.warning(self, 'Erro no login', 'Email e/ou senha incorretos')
            else:

                QMessageBox.warning(self, 'Erro no login', 'Ocorreu um erro')
        except Exception as e:
            print(f"Error during login: {e}")
            QMessageBox.warning(self,f"Ocorreu um erro: {e}")



    def callback_cadastro(self):

        '''
        Conexão responsável pelo cadastro do usuário

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''
        opcao = '2'
        self.client_socket.send(opcao.encode())

        first_name = self.cadastroPage.first_name.text()
        second_name = self.cadastroPage.second_name.text()
        email_or_phone = self.cadastroPage.email_or_phone.text()
        password = self.cadastroPage.password.text()
        confirm_password = self.cadastroPage.confirm_password.text()
        dia = int(self.cadastroPage.dia.currentText())
        mes = int(self.cadastroPage.mes.currentText())
        ano = int(self.cadastroPage.ano.currentText())
        data_nascimento = str(dia) + '/' + str(mes) + '/' + str(ano)


        string = f"{first_name},{second_name},{email_or_phone},{password},{data_nascimento}"


        if first_name == '' or second_name == '' or email_or_phone == '' or password == '' or confirm_password == '':
            QMessageBox.warning(self, 'Erro no cadastro', 'Preencha todos os campos')
            return
        if password != confirm_password:
            QMessageBox.warning(self, 'Erro no cadastro', 'Senhas não conferem')
            return

        self.client_socket.send(string.encode())

        try:

            retornooo = self.client_socket.recv(1024).decode()

            if retornooo == '1':

                self.stacked_widget.setCurrentIndex(0)
                QMessageBox.warning(self, 'Cadastro', 'Cadastro realizado com sucesso')
            elif retornooo == '-2':

                QMessageBox.warning(self, 'Email já existe', 'Email já existe')
            else:

                QMessageBox.warning(self, 'Erro no cadastro', 'Ocorreu um erro')
        except Exception as e:
            print(f"Erro durante cadastro: {e}")
            QMessageBox.warning(self, "Erro no cadastro", f"Ocorreu um erro: {e}")
            return

        self.cadastroPage.first_name.clear()
        self.cadastroPage.second_name.clear()
        self.cadastroPage.email_or_phone.clear()
        self.cadastroPage.password.clear()
        self.cadastroPage.confirm_password.clear()
        self.cadastroPage.dia.setCurrentIndex(0)
        self.cadastroPage.mes.setCurrentIndex(0)
        self.cadastroPage.ano.setCurrentIndex(0)


    def buscar_noticiasTela(self):

        '''
        Conexão responsável por mostrar na tela as notícias retornadas para o cliente

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''
        opcao = '3'
        self.client_socket.send(opcao.encode())

        keyword = self.tela_02.key_word.text()
        qntd_tela = int(self.tela_02.qntd_tela.currentText())
        section = self.tela_02.filter_tela.currentText().lower()

        if keyword == '':
            QMessageBox.warning(self, 'Erro na busca', 'Digite uma palavra-chave')
            return
        if qntd_tela == '':
            QMessageBox.warning(self, 'Erro na busca', 'Digite uma quantidade de notícias')
            return
        if section == '':
            QMessageBox.warning(self, 'Erro na busca', 'Selecione uma seção')
            return


        string = f"{keyword},{qntd_tela},{section}"

        self.client_socket.send(string.encode())#1
        retorno = self.client_socket.recv(1024).decode()#2
        self.client_socket.send('1'.encode())#3

        if retorno == '1':
            self.stacked_widget.setCurrentIndex(2)
            noticias = self.client_socket.recv(4096).decode()

            self.tela_02.news_display.setPlainText("")
            self.tela_02.news_display.setText(noticias)
            self.tela_02.news_display.setHtml(noticias)

            QMessageBox.warning(self, 'Busca', 'Busca realizada com sucesso')

            
                
        elif retorno == '-1':
            noticias = self.client_socket.recv(1024).decode()
            self.stacked_widget.setCurrentIndex(2)
            QMessageBox.warning(self, 'Ocorreu um erro na busca')
            self.tela_02.news_display.setText(noticias)
        elif retorno == '-2':
            self.stacked_widget.setCurrentIndex(2)
            QMessageBox.warning(self, 'Erro na busca', 'Ocorreu um erro na palavra chave')

        self.tela_02.key_word.clear()
        

    def programaEnvioEmail(self):
        
        '''
        Conexão responsável pela programação de envio por email

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''
        quantidade = self.programarEnvio.qntdTela.currentText()
        keyword = self.programarEnvio.digitarInfo.text()
        frenquencia = self.programarEnvio.frequenciaEmails.currentText()
        sectio = self.programarEnvio.section.currentText()
        emai = self.mainPage.email_or_phone.text()

        if quantidade == '' or keyword == '' or frenquencia == '' or sectio == '':
            QMessageBox.warning(self, 'Erro ao programar envios', 'Não pode conter campos vazios')
            return

        opcao = '4'
        self.client_socket.send(opcao.encode())
        
        string = f"{quantidade},{keyword},{frenquencia},{sectio},{emai}"
        self.client_socket.send(string.encode())#1
            
        retorno = self.client_socket.recv(1024).decode()#2

        if retorno == '1':
                
            QMessageBox.warning(self, 'Programação de emails', 'Operação realizada com sucesso')
        elif retorno == '-1':

            QMessageBox.warning(self, 'Programação de emails', 'Falha na operação')

        self.programarEnvio.digitarInfo.clear()
        
    def programarEnvioTela(self):

        '''
        Conexão responsável por chamar a tela de programar envios para email

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''
        self.stacked_widget.setCurrentIndex(5)

    def callback_exit(self):

        '''
        Conexão responsável por sair da aplicação

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''
        opcao = '-1'
        self.client_socket.send(opcao.encode())
        self.client_socket.close()
        exit(1)

    def about_uss_funcao(self):

        '''
        Conexão responsável pela chamada de uma tela para confirmação da saída
        da aplicação

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''
        self.stacked_widget.setCurrentIndex(3)

    def confirmarSaidaFuncao(self):

        '''
        Conexão responsável pela chamada da tela de confirmação de logout

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        '''
        self.stacked_widget.setCurrentIndex(4)
        
    def telaDeBusca(self):

        '''
        Conexão responsável pela chamada da tela de pesquisas

        Parameters
        ----------

        Returns
        -------

        Raises
        ------        
        '''
        self.stacked_widget.setCurrentIndex(2)



ip = 'localhost'
#192.168.18.46
port = 9009

addr = (ip, port)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect(addr)

print('A conexão funcionou :)')
if __name__ == '__main__':
    app = QApplication([' '])
    window = LoginPage(client_socket)
    app.exec()
