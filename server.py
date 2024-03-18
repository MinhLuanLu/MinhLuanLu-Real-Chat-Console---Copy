import socket
import threading
import json
import socketio
import socket


SERVER_IP = socket.gethostbyname(socket.gethostname())
#SERVER_IP = ''
print(f'SERVER IP: {SERVER_IP}')
HOST = SERVER_IP
PORT = 8080
LIMIT_user = 100
ACTIVE_USER_list = []  # Will store tuples of (username, client_socket)
CONVERSATION = []
dialog = ''
IP_address_list = []





def get_username_from_client(client_socket):
    global ACTIVE_USER_list
    while True:
        try:
            username = client_socket.recv(2048).decode('utf-8') # GEt username from Flask
            if username != '':
                ACTIVE_USER_list.append((username, client_socket))
                print(f'{username} is Online...')
               
                break
            else:
                print('Error !!! Can not receive username....')
        except Exception as e:
            print(f"Error receiving username: {e}")
            break

def receive_messages_from_client(client_socket, username):
    global dialog

   
    while True:
        try:
            message = client_socket.recv(2048).decode('utf-8')
            if message:
                dialog = f'{username}: {message}'
                print(f"MESSAGE FROM SERVER: {dialog}") # Print The Username and Message in Server
                CONVERSATION.append(dialog) # Add the Username and Message to the CONVERSATION
                #client_socket.sendall(json.dumps(CONVERSATION).encode()) ## send the CONVERSATION to Flask wit Json format
                if dialog: # if any message that server has been recived
                    print('ADD MESSAGE TO CONVERSTAION....')
                    
                    send_messages_to_all_user() # Broadcast messages to all active clients in by using Python-Sockets
                    
                    send_dialog_to_flask() # Send messages to all active IP Address by using Socketio

                    print(f'Conversation History (Server): {CONVERSATION}') # Print Conversation
                  
            else:
                print('ERROR to get message')
                break
                
        except Exception as e:
            print(f"Error receiving message from {username}: {e}")
            break

def send_messages_to_all_user():
    send_message = dialog
    for _, client_socket in ACTIVE_USER_list:
        send_msg_to_client(client_socket, send_message)


def send_msg_to_client(client_socket, message):
    client_socket.sendall(message.encode())



def socketio_connection(address): # Connect to Flask by using Socketio
    send_dialog = dialog
    sio = socketio.Client()
   
    @sio.event ## Wait for the even connect happen then do something
    def connect():
        connect = f'Connected to Flask-SocketIO server {address}'
        print(connect)
        sio.emit('connection_status', connect)
        sio.emit('dialog', send_dialog)
        
    @sio.event # Wait for the even Disconnect happen then do something
    def disconnect():
        disconnect = 'Disconnected from Flask-SocketIO server'
        print(disconnect)
        sio.emit('connection_status', disconnect)
    
    try:
        sio.connect(f'http://{address}:5000')

    except Exception as e:
        print(f"Failed to connect to {address}: {e}")
    
def send_dialog_to_flask():
    threads = []
    for address in IP_address_list: # loop through the IP list
        thread = threading.Thread(target=socketio_connection, args=(address,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    
        

def main():
    global CONVERSATION
    global ip_address
    global port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        try:
            server.bind((HOST, PORT))
            print('Server waiting for connection...')
           
        except Exception as e:
            print(f'Error binding the server: {e}')
            return

        server.listen(LIMIT_user)
      
        while True:
            client_socket, address = server.accept()
            print(f'Connection to {address} is successful')

            get_ip_address_and_port = client_socket.getsockname() #### GEt the ip address and the port from client that connect to Server
            ip_address = address[0]
            port = get_ip_address_and_port[-1]
            IP_address_list.append((ip_address)) # ADD the IP Address to List
            print(f'IP Adrdress Connecting to Server: {IP_address_list}')
    
            #### Try to Update the CONVERSATION list in Server when the connection is successfully

            update_CONVERSATION = client_socket.sendall(json.dumps(CONVERSATION).encode())
            if update_CONVERSATION!= '':              
                print('Update messages in CONVERSATION list in Server to Flask...')
                update_CONVERSATION
            
                threading.Thread(target=socketio, args=(address, ))
                
            else:
                print('No messages in CONVERSATION list from Server right now...')
                update_CONVERSATION 
                threading.Thread(target=socketio, args=(address, ))

            ###################################################
            get_username_from_client(client_socket)

            username = ACTIVE_USER_list[-1][0]
            threading.Thread(target=receive_messages_from_client, args=(client_socket, username)).start()

if __name__ == "__main__":
    threading.Thread(target=main).start()
    
   

