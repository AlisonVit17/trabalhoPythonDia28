import socket
import threading
import time
from PyQt5.QtWidgets import QApplication
import mysql.connector

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
                if opcao.decode() == '1':
                    
                    email = self.conexao.recv(1024).decode()
                    senha = self.conexao.recv(1024).decode()
                    enviar = self.verificaLogin(email, senha)
                    self.conexao.send(enviar.encode())
                if opcao.decode() == '-1':

                    break
                else:
                    
                    pass
        except:
            
            pass
        print('Disconnected')
        self.conexao.close()
        self.startEnd.set()        
    def verificaLogin(self, email, senha):
        retorno = '0'

        conexao = self.conectar_banco()
        cursor = conexao.cursor()

        query = "SELECT * FROM usuarios WHERE email = %s AND senha = %s;"
        cursor.execute(query, (email, senha))
        usuario = cursor.fetchone()

        cursor.close()
        conexao.close()

        if usuario:
            retorno = '1'

        return retorno;
    def conectar_banco(self):

        conexao = mysql.connector.connect(
            host= "localhost",
            user= "root",
            password= "",
            database= "project_webScraping"
        )
        return conexao
    

host = ''

port = 9007

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
