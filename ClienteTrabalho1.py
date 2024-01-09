import socket

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget
from PyQt5.uic import loadUi
from qdarkstyle import load_stylesheet_pyqt5


class LoginPage(QMainWindow):
    _quantEmailsComProgramacoes = 0

    def __init__(self, client_socket):
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
        self.mainPage.about_us.clicked.connect(self.about_uss)
        self.tela_02.logout_btn.clicked.connect(self.confirmarSaida)
        self.tela_02.search_btn.clicked.connect(self.buscar_noticiasTela)
        self.tela_02.envioProgramado.clicked.connect(self.confirmarSaida)
        self.tela_02.envioProgramado.clicked.connect(self.programarEnvioTela)
        self.programarEnvio.voltarMostrarTela.clicked.connect(self.confirmarSaida)
        self.programarEnvio.programar.clicked.connect(self.programaEnvio)
        self.programarEnvio.testarEvios.clicked.connect(self.programaEnvio)
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

        opcao = '2'
        self.stacked_widget.setCurrentIndex(1)

    def voltar_main_page(self):
        opcao = '1'
        self.stacked_widget.setCurrentIndex(0)
        self.mainPage.password.clear()
        self.mainPage.email_or_phone.clear()

    def toggle_theme(self):
        selected_theme = self.mainPage.light_dark.currentText()
        self.apply_theme(selected_theme)

    def apply_theme(self, theme_name):
        opcao = '0'
        self.client_socket.send(opcao.encode())
        if theme_name == "Dark":
            self.setStyleSheet(load_stylesheet_pyqt5())
        else:
            self.setStyleSheet("")

    def callback_login(self):
        opcao = '1'
        self.client_socket.send(opcao.encode())

        email = self.mainPage.email_or_phone.text()
        senha = self.mainPage.password.text()

        if email == '' or senha == '':
            QMessageBox.warning(self, 'Erro no login', 'Email e/ou senha incorretos')
            return

        string = f"{email},{senha}"

        try:
            self.client_socket.send(string.encode())
            retorno = self.client_socket.recv(1024).decode()

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
                # print("Cadastro realizado com sucesso.")
                self.stacked_widget.setCurrentIndex(0)
                QMessageBox.warning(self, 'Cadastro', 'Cadastro realizado com sucesso')
            elif retornooo == '-2':
                # print("Email já existe.")
                QMessageBox.warning(self, 'Email já existe', 'Email já existe')
            else:
                # print("Erro no cadastro.")
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
        self.client_socket.send(string.encode())


        try:
            retorno = self.client_socket.recv(1024).decode()
        except Exception as e:
            print(f"Error during login: {e}")
            QMessageBox.warning(self, "Erro no login", f"Ocorreu um erro: {e}")
            return

        if retorno == '1':
            self.stacked_widget.setCurrentIndex(2)
            QMessageBox.warning(self, 'Busca', 'Busca realizada com sucesso')
        elif retorno == '-1':
            QMessageBox.warning(self, 'Ocorreu um erro na busca')
        elif retorno == '-2':
            QMessageBox.warning(self, 'Erro na busca', 'Ocorreu um erro na palavra chave')
        self.tela_02.key_word.clear()
        self.tela_02.qntd_tela.clear()


    def programaEnvio(self):
        opcao = '4'
        self.client_socket.send(opcao.encode())

        quantidade = self.programarEnvio.qntdTela.currentText()
        lingua = self.programarEnvio.lingua_tela.currentText()
        frenquencia = self.programarEnvio.frequenciaEmails.currentText()

        if quantidade == '':
            QMessageBox.warning(self, 'Erro na busca', 'Digite uma quantidade de notícias')
            return
        if lingua == '':
            QMessageBox.warning(self, 'Erro na busca', 'Selecione uma lingua')
            return
        if frenquencia == '':
            QMessageBox.warning(self, 'Erro na busca', 'Selecione uma frequência')
            return

        string = f"{quantidade},{lingua},{frenquencia}"
        self.client_socket.send(string.encode())

        try:
            retorno = self.client_socket.recv(1024).decode()
        except Exception as e:
            print(f"Error during login: {e}")
            QMessageBox.warning(self, "Erro no login", f"Ocorreu um erro: {e}")
            return

        if retorno == '1':
            self.stacked_widget.setCurrentIndex(5)
            QMessageBox.warning(self, 'Busca', 'Busca realizada com sucesso')
        elif retorno == '-1':
            QMessageBox.warning(self, 'Ocorreu um erro na busca')
        elif retorno == '-2':
            QMessageBox.warning(self, 'Erro na busca', 'Ocorreu um erro na palavra chave')

        self.programarEnvio.key_word.clear()
        self.programarEnvio.qntd_tela.clear()



    def programarEnvioTela(self):
        opcao = '4'
        self.client_socket.send(opcao.encode())
        self.stacked_widget.setCurrentIndex(5)


    def callback_exit(self):
        opcao = '-1'
        self.client_socket.send(opcao.encode())
        self.client_socket.close()

    def about_uss(self):
        opcao = '0'
        self.client_socket.send(opcao.encode())


    def confirmarSaida(self):
        opcao = '0'
        self.client_socket.send(opcao.encode())

        teste = '1'

        self.client_socket.send(teste.encode())

        resposta_servidor = self.client_socket.recv(1024).decode()

        if resposta_servidor == '1':
            QMessageBox.warning(self, 'Continua', 'Continuando...')
            self.stacked_widget.setCurrentIndex(4)
        elif resposta_servidor == '2':
            QMessageBox.warning(self, 'Sair', 'Saindo...')
            self.stacked_widget.setCurrentIndex(0)
        else:
            print("deu ruim.")
            return

    def telaDeBusca(self):
        opcao = '3'
        # self.client_socket.send(opcao.encode())
        self.stacked_widget.setCurrentIndex(2)



ip = '192.168.18.46'
port = 9005

addr = (ip, port)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect(addr)

print('A conexão funcionou :)')
if __name__ == '__main__':
    app = QApplication([' '])
    window = LoginPage(client_socket)
    app.exec()
