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

        while True:

            opcao = self.conexao.recv(1024)
            if opcao.decode() == '1':
                
                email = self.conexao.recv(1024).decode()
                senha = self.conexao.recv(1024).decode()
                enviar = self.verificaLogin(email, senha)
                self.conexao.send(enviar.encode())
            if opcao.decode() == '-1':

                print('Disconnected')
                self.conexao.close()
                self.startEnd.set()
                break
            else:
                
                pass

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
            database= "project_webscraping"
        )
        return conexao
    

host  = ''   #se eu deixar em branco eu vou poder aceitar conexao de qualquer lugar

port = 9000 # valores menores que 1024 sao utilizadas pelo sistema o ideial e rodar em um porta maior que > 24

addr = (host, port)

serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #cria o socket
serv_socket.bind(addr) #define a porta e quais ips podem se conectar com o servidor (deixar aberta a conexao)
serv_socket.listen(10) #define o limite de conexoes

#precisa do ip, e da porta para os computadores se comunicar 

while(True):
    
    try:
        
        print('aguardando conexao...')
        con, cliente = serv_socket.accept() #servidor aguardando conexao
        cliente = ClientThread(con, cliente)
        cliente.start()
        #enviar = input('digite uma mensagem para enviar ao cliente: ')
        #con.send(enviar.encode()) #enviar uma mensagem para o cliente
    except:
        con, cliente = serv_socket.accept() #servidor aguardando conexao
