import socket
import threading


#SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_IP = '192.53.120.97'
PORT = 62023

def send_msg_to_server(client):
    while True:
        message = input('Message: ')
        if message != '':
            client.sendall(message.encode())
        else:
            print("Message is Emty...")

def connect_to_server(client):

    username = input('Enter Username: ')
    if username != '':
        client.sendall(username.encode())
    else:
        print('Username is Emty !!!')

    
    threading.Thread(target=get_message_from_server,args=(client, )).start()
    send_msg_to_server(client)
    

def get_message_from_server(client):
  
    while True:
        message = client.recv(2048).decode()
        if message != '':
            print(message)
        else:
            print('No message !!!')
   

def main():
    connection_status = ''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((SERVER_IP, PORT))
            connection_status = 'Connection is Successfully'
            connect_to_server(client)
        except:
            connection_status = 'NO Connection had Found !!!'
            print(connection_status)
    return connection_status


if __name__ == '__main__':
    main()