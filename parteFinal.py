from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget
from PyQt5.uic import loadUi
from datetime import date

from qdarkstyle import load_stylesheet_pyqt5

import mysql.connector

import email.message
import smtplib
import requests

from bs4 import BeautifulSoup

class Pessoa:

    _quantPessoas = 0

    def __init__(self, firstName, lastName, email, senha, dia, mes, ano):
        self._firstName = firstName
        self._lastName = lastName
        self._email = email
        self._senha = senha
        self._dia = dia
        self._mes = mes
        self._ano = ano
        Pessoa._quantPessoas += 1

    def verifica(self, email):
        if email == self._email:

            return True
        else:

            return False

    # def verificaLogin(self, email, senha):
    #
    #     if senha == self._senha and email == self._email:
    #
    #         return True
    #     else:
    #
    #         return False

    @property
    def firstName(self):
        return self._firstName

    @firstName.setter
    def firstName(self, _):
        print('Não é permitido a alteração de qualquer campo!')

    @property
    def lastName(self):
        return self._lastName

    @lastName.setter
    def lastName(self, _):
        print('Não é permitido a alteração de qualquer campo!')

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, _):
        print('Não é permitido a alteração de qualquer campo!')

    @property
    def senha(self):
        return False

    @senha.setter
    def senha(self, _):
        print('Não é permitido a alteração de qualquer campo!')

    @property
    def dia(self):
        return self._dia

    @dia.setter
    def dia(self, _):
        print('Não é permitido a alteração de qualquer campo!')

    @property
    def mes(self):
        return self._mes

    @mes.setter
    def mes(self, _):
        print('Não é permitido a alteração de qualquer campo!')

    @property
    def ano(self):
        return self._ano

    @ano.setter
    def ano(self, _):
        print('Não é permitido a alteração de qualquer campo!')


class LoginPage(QMainWindow):

    _quantEmailsComProgramacoes = 0

    def __init__(self):
        super().__init__()
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
        self._pessoas = []
        self.programacoesDeEnvio = {}
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
        self.cadastroPage.cadastrar_button.clicked.connect(self.cadastrar)
        self.cadastroPage.voltar_button.clicked.connect(self.voltar_main_page)
        self.mainPage.login_button.clicked.connect(self.callback_login)
        self.mainPage.exit_button.clicked.connect(self.callback_exit)
        self.tela_02.logout_btn.clicked.connect(self.confirmarSaida)
        self.tela_02.search_btn.clicked.connect(self.buscar_noticiasTela)
        self.mainPage.about_us.clicked.connect(self.about_uss)
        self.confirmaSaida.logout.clicked.connect(self.voltar_main_page)
        self.confirmaSaida.cancel.clicked.connect(self.telaDeBusca)
        self.about_us.back_butt.clicked.connect(self.voltar_main_page)
        self.tela_02.envioProgramado.clicked.connect(self.telaProgramarEnvio)
        self.programarEnvio.voltarMostrarTela.clicked.connect(self.telaDeBusca)
        self.programarEnvio.programar.clicked.connect(self.emailProgramado)
        self.programarEnvio.testarEvios.clicked.connect(self.buscar_noticiasEmail)

        self.mainPage.email_or_phone.setPlaceholderText('Email')
        self.mainPage.password.setPlaceholderText('Password')
        self.cadastroPage.first_name.setPlaceholderText('First Name')
        self.cadastroPage.second_name.setPlaceholderText('Last Name')
        self.cadastroPage.email_or_phone.setPlaceholderText('Email')
        self.cadastroPage.password.setPlaceholderText('Password')
        self.cadastroPage.confirm_password.setPlaceholderText('Confirm Password')
        self.tela_02.key_word.setPlaceholderText('Enter with the key')

        self.tela_02.qntd_tela.addItems(["1", "2", "3", "4", "5"])
        #self.tela_02.lingua_tela.addItems(["Português", "Inglês"])
        #self.tela_02.prazo.addItems(["Diario", "Semanal", "Mensal"])
        self.tela_02.filter_tela.addItems(["Home", "World", "Local", "Business", "Technology"])
        self.programarEnvio.qntdTela.addItems(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.programarEnvio.lingua_tela.addItems(["Português", "Inglês"])
        self.programarEnvio.digitarInfo.setPlaceholderText('Enter with the key')
        self.mainPage.light_dark.addItems(["Light", "Dark"])

    def emailProgramado(self):
        email = self.mainPage.email_or_phone.text()
        assunto = self.programarEnvio.digitarInfo.text()
        quantidadeDeInformacoes = int(self.programarEnvio.qntdTela.currentText())
        linguagem = str(self.programarEnvio.lingua_tela.currentText().lower())
        umDiaOuSemanaToda = str(self.programarEnvio.frequenciaEmails.currentText())
        frequencia = 7
    
        if umDiaOuSemanaToda == 'Segunda-feira':

            frequencia = 0
        elif umDiaOuSemanaToda == 'Terça-feira':

            frequencia = 1
        elif umDiaOuSemanaToda == 'Quarta-feira':

            frequencia = 2
        elif umDiaOuSemanaToda == 'Quinta-feira':

            frequencia = 3
        elif umDiaOuSemanaToda == 'Sexta-feira':

            frequencia = 4
        elif umDiaOuSemanaToda == 'Sábado':

            frequencia = 5
        elif umDiaOuSemanaToda == 'Domingo':

            frequencia = 6

        if email not in self.programacoesDeEnvio.keys():
            self.programacoesDeEnvio[email] = [[], [], [], []]
            self.programacoesDeEnvio[email][0].append(assunto)
            self.programacoesDeEnvio[email][1].append(quantidadeDeInformacoes)
            self.programacoesDeEnvio[email][2].append(linguagem)
            self.programacoesDeEnvio[email][3].append(frequencia)
        else:
            self.programacoesDeEnvio[email][0].append(assunto)
            self.programacoesDeEnvio[email][1].append(quantidadeDeInformacoes)
            self.programacoesDeEnvio[email][2].append(linguagem)
            self.programacoesDeEnvio[email][3].append(frequencia)

        QMessageBox.warning(self, 'Programar envio', 'programação de envio realizada com sucesso')
        LoginPage._quantEmailsComProgramacoes += 1

        for i in self.programacoesDeEnvio.keys():
            print(self.programacoesDeEnvio[i])
    def telaProgramarEnvio(self):
        self.stacked_widget.setCurrentIndex(5)

    def telaDeBusca(self):
        self.clear_buscaNoticias()
        self.stacked_widget.setCurrentIndex(2)

    def confirmarSaida(self):
        self.stacked_widget.setCurrentIndex(4)

    def toggle_theme(self):
        selected_theme = self.mainPage.light_dark.currentText()
        self.apply_theme(selected_theme)

    def apply_theme(self, theme_name):
        if theme_name == "Dark":
            self.setStyleSheet(load_stylesheet_pyqt5())
        else:
            self.setStyleSheet("")

    def callback_login(self):
        email = self.mainPage.email_or_phone.text()
        senha = self.mainPage.password.text()

        conexao = self.conectar_banco()
        cursor = conexao.cursor()

        query = "SELECT * FROM usuarios WHERE email = %s AND senha = %s;"
        cursor.execute(query, (email, senha))
        usuario = cursor.fetchone()

        cursor.close()
        conexao.close()

        if usuario:
            self.stacked_widget.setCurrentIndex(2)
            QMessageBox.warning(self, 'Login', 'Login realizado com sucesso')
        else:
            QMessageBox.warning(self, 'Erro no login', 'Email e/ou senha incorretos')

    def callback_exit(self):
        exit(1)

    def mostrar_cadastro(self):
        self.stacked_widget.setCurrentIndex(1)

    def voltar_main_page(self):
        self.stacked_widget.setCurrentIndex(0)
        self.mainPage.password.clear()
        self.mainPage.email_or_phone.clear()

    def about_uss(self):
        self.stacked_widget.setCurrentIndex(3)

    def conectar_banco(self):

        conexao = mysql.connector.connect(
            host= "localhost",
            user= "root",
            password= "",
            database= "project_webscraping"
        )
        return conexao

    def cadastrar(self):
        first_name = self.cadastroPage.first_name.text()
        second_name = self.cadastroPage.second_name.text()
        email_or_phone = self.cadastroPage.email_or_phone.text()
        password = self.cadastroPage.password.text()
        confirm_password = self.cadastroPage.confirm_password.text()
        dia = int(self.cadastroPage.dia.currentText())
        mes = int(self.cadastroPage.mes.currentText())
        ano = int(self.cadastroPage.ano.currentText())


        if (dia == 31 and (mes == 4 or mes == 6 or mes == 10 or mes == 11)) or (dia >= 29 and mes == 2):

            QMessageBox.warning(self, 'Erro no cadastro', 'O mês selecionado não possui essa quantidade de dias')
        else:
            email_list = list(email_or_phone)

            if '@' not in email_list:

                QMessageBox.warning(self, 'Erro', 'O email não possui endereço')
            elif '@' in email_list:

                lista = email_or_phone.split('@')
                if ((lista[1] == 'gmail.com' or lista[1] == 'hotmail.com' or lista[1] == 'outlook.com')
                        and email_list[0] != '@'):
                    try:

                        lista[2]
                    except:

                        if password == confirm_password and len(password) > 10:

                            booleano = False
                            for i in self._pessoas:

                                booleano = i.verifica(email_or_phone)
                                if booleano is True:
                                    QMessageBox.warning(self, 'Erro no cadastro', 'O email já está cadastrado')
                                    break

                            if (booleano is not True and first_name != '' and
                                    password != ''):
                                conexao = self.conectar_banco()
                                cursor = conexao.cursor()

                                insert_query = "INSERT INTO usuarios (first_name, second_name, email, senha, dia, mes, ano) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                                user_data = (first_name, second_name, email_or_phone, password, dia, mes, ano)
                                cursor.execute(insert_query, user_data)

                                conexao.commit()

                                cursor.close()
                                conexao.close()

                                QMessageBox.warning(self, 'Cadastro', 'Cadastro realizado com sucesso')
                            else:
                                QMessageBox.warning(self, 'Erro no Cadastro', 'Não é permitido deixar'
                                                                              ' campos vazios')

                        else:
                            QMessageBox.warning(self, 'Erro no cadastro', 'As senhas não coincidem ou a mesma'
                                                                          ' possui menos de 10 caracteres')

                else:
                    QMessageBox.warning(self, 'Erro', 'O email não possui endereço, ou possui '
                                                      'algum caractere inválido')
            self.clear_cadastro_fields()

    def clear_cadastro_fields(self):
        self.cadastroPage.first_name.clear()
        self.cadastroPage.second_name.clear()
        self.cadastroPage.email_or_phone.clear()
        self.cadastroPage.password.clear()
        self.cadastroPage.confirm_password.clear()

    def buscar_noticiasTela(self):
        keyword = self.tela_02.key_word.text()
        qntd_tela = int(self.tela_02.qntd_tela.currentText())
        section = self.tela_02.filter_tela.currentText().lower()

        if keyword:
            # # Defina o idioma com base na escolha do usuário
            # idioma = "en-US"  # Inglês por padrão
            # if lingua == "português":
            #     idioma = "pt-BR"

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
                self.exibir_noticias(matching_news)

            else:
                self.tela_02.news_display.setPlainText("Erro ao buscar notícias.")
        else:
            self.tela_02.news_display.setPlainText("Insira uma palavra-chave para buscar notícias.")

    def exibir_noticias(self, noticias): #noticias é uma lista, talvez vazia...

        self.tela_02.news_display.setPlainText("")
        if noticias:

            news_text = ""
            for news in noticias:

                news_text += f'Título: {news["title"]}<br>'
                news_text += f'Link: <a href="{news["link"]}">{news["link"]}</a><br><br>'
            self.tela_02.news_display.setOpenExternalLinks(True)
            self.tela_02.news_display.setHtml(news_text)
        else:
            self.tela_02.news_display.setPlainText("Nenhuma notícia encontrada com a palavra-chave no título.")

    def buscar_noticiasEmail(self):

        hoje = date.today()
        email = ""
        for i in self.programacoesDeEnvio.keys():
            listaNoticias = []
            quantInfo = []
            assunto = []
            idioma = []
            for a in range(len(self.programacoesDeEnvio[i][0])):
                if (hoje.weekday() == self.programacoesDeEnvio[i][3][a] or self.programacoesDeEnvio[i][3][a] == 7):
                    email = i
                    quantInfo.append(self.programacoesDeEnvio[i][1][a])
                    assunto.append(self.programacoesDeEnvio[i][0][a])
                    idioma.append(self.programacoesDeEnvio[i][2][a])

            for a in range(len(quantInfo)):
                print('Cheguei no dia')
                if assunto[a]:
                    api_key = '1564acb7dbc747d3858772371c9fb9c1'
                    print(assunto[a], quantInfo[a], api_key)
                    url = f'https://api.worldnewsapi.com/search-news?text={assunto[a]}&number={quantInfo[a]}&api-key={api_key}'

                    if idioma[a] == "português":
                        url += '&language=pt'
                    try:
                        response = requests.get(url)

                        if response.status_code == 200:
                            listaNoticias.append(response.json())
                        else:
                            self.tela_02.news_display.setPlainText("Erro ao buscar notícias.")
                            print('Não deu certo buscar a notícia')
                    except Exception as e:
                        self.tela_02.news_display.setPlainText(f"Erro: {str(e)}")
                else:
                    self.tela_02.news_display.setPlainText("Insira uma palavra-chave para buscar notícias.")

            if listaNoticias != []:
                print(i)
                self.enviaEmails(listaNoticias, i)
                print('Emails enviados com sucesso!')

    def envia_Email(self, emai, news_text):
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

    def enviaEmails(self, listaNoticias, email):
        news_text = ""
        for noticias in listaNoticias:
            if 'news' in noticias:
                news = noticias['news']
                if news:
                    for i, article in enumerate(news):
                        news_text += f"Notícia {i + 1}:\n"
                        news_text += f"Título: {article.get('title', 'N/A')}\n"
                        news_text += f"Link: {article.get('url', 'N/A')}\n\n"
                    news_text += "\n\n"
                else:
                    news_text +="Nenhuma notícia encontrada."
            else:
                news_text +="Nenhuma notícia encontrada."

        if news_text != "":
            self.envia_Email(email, news_text)

if __name__ == '__main__':
    app = QApplication([' '])
    window = LoginPage()
    app.exec()

'''
O que o sistema deve fazer depois da pessoa logar... 
E ajeitar os problemas do que está aqui até agora
Precisa implementar as funcionalidades depois da pessoa logar.
Até próxima quinta...
Quinta tem banco de dados com python
'''

#comentario da sorte, se voce leu eh porque deu certo
