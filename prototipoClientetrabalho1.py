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
        self.mainPage = loadUi('mainPage.ui')
        self.cadastroPage = loadUi('register.ui')
        self.tela_02 = loadUi('tela_02.ui')
        self.programarEnvio = loadUi('programarTela.ui')
        self.about_us = loadUi('about_us.ui')
        self.confirmaSaida = loadUi('confirmaSaida.ui')
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

        self.mainPage.createAccount_button.clicked.connect(self.mostrar_cadastro)#
        self.cadastroPage.voltar_button.clicked.connect(self.voltar_main_page) #
        self.mainPage.login_button.clicked.connect(self.callback_login) #
        self.mainPage.exit_button.clicked.connect(self.callback_exit) #
        self.mainPage.about_us.clicked.connect(self.about_uss) #
        self.tela_02.logout_btn.clicked.connect(self.confirmarSaida) #
        self.about_us.back_butt.clicked.connect(self.voltar_main_page) #
        self.confirmaSaida.logout.clicked.connect(self.voltar_main_page) #
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

        opcao = '0'
        self.client_socket.send(opcao.encode())
        self.stacked_widget.setCurrentIndex(1)

    def voltar_main_page(self):
        
        opcao = '0'
        self.client_socket.send(opcao.encode())
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
            email = 'a'
            senha = 'a'
            
        self.client_socket.send(email.encode())
        self.client_socket.send(senha.encode())
        certo = self.client_socket.recv(1024).decode()

        if certo == '1':
            
            self.stacked_widget.setCurrentIndex(2)
            QMessageBox.warning(self, 'Login', 'Login realizado com sucesso') 
        else:
            
            QMessageBox.warning(self, 'Erro no login', 'Email e/ou senha incorretos')

    def callback_exit(self):
        opcao = '-1'
        self.client_socket.send(opcao.encode())
        self.client_socket.close() #fecha conexao
        exit(1)

    def about_uss(self):
        opcao = '0'
        self.client_socket.send(opcao.encode())
        self.stacked_widget.setCurrentIndex(3)

    def confirmarSaida(self):
        opcao = '0'
        self.client_socket.send(opcao.encode())
        self.stacked_widget.setCurrentIndex(4)

    def telaDeBusca(self):

        opcao = '0'
        self.client_socket.send(opcao.encode())
        self.stacked_widget.setCurrentIndex(2)

#ip = input('digite )
ip = 'localhost' #ip do servidor (ip da maquina)
#Ip da minha máquina: 192.168.1.13
#10.180.44.143
port = 9000
#port = 7001
addr = ((ip, port)) #deefine a tupla de endereco
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect(addr) #realiza a conexao

print('A conexão funcionou :)')
if __name__ == '__main__':
    app = QApplication([' '])
    window = LoginPage(client_socket)
    app.exec()

#$ fazer a desconexxao do servidor, o servidor vai aguardar uma nova conexao esperando um novo cliente
