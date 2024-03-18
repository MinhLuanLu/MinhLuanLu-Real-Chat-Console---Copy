
from flask import Flask, render_template, request, redirect, url_for, session
import socket
from flask_socketio import SocketIO,emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'susaa'
socketio = SocketIO(app)

#SERVER_IP = socket.gethostbyname(socket.gethostname())
MY_IP = socket.gethostbyname(socket.gethostname())
SERVER_IP = '192.53.120.128'

PORT = 8080
client_socket = None  # Global variable to store client socket
CONVERSATION = []

live_CONVERSATON = []


@app.route('/', methods=['GET', 'POST'])   # Get Username from Clients
def join():
    global username
    if request.method == 'POST':
        username = request.form.get('username_input')
        if username != '':
            print(f'{username} joined')
           
            
            return redirect(url_for('connect_to_SERVER', username=username))
        else:
            return 'NO username'
    return render_template('join.html')



@app.route('/connect_to_SERVER')  # Handle Connection to Server....
def connect_to_SERVER():
    global client_socket
    global send_username_to_server
    global connection_status
    global CONVERSATION
    global check_any_CONVERSATION_from_server
    global update_any_CONVERSATION_from_server
    global convert_the_list_to_string 

    
    send_username_to_server = username
    connection_status = ''
   
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, PORT))
        connection_status = 'Connection is successful'
        
        if send_username_to_server != "":
            client_socket.sendall(send_username_to_server.encode()) # Send username to Server....
            print(f'Username [{send_username_to_server}] has been sent To Server...')
            
        ##################### GET THE UPDATE CONVERSATION FROM SERVER. Check is there any messages in CONVERSATION list FROM SERVER...
            
            update_any_CONVERSATION_from_server = client_socket.recv(2048).decode('utf-8') # Try to get any messasges in CONVERSATION list with Json format  that are exsist already in Server after Socket Connection Successful
            convert_the_CONVERSATION_from_server_to_list = json.loads(update_any_CONVERSATION_from_server) ## Convert the Json format to a list
            convert_the_list_to_string = ''.join(convert_the_CONVERSATION_from_server_to_list) #Convert the List to Emtry String

            check_any_CONVERSATION_from_server = convert_the_CONVERSATION_from_server_to_list
            if convert_the_list_to_string != '':
                CONVERSATION = convert_the_CONVERSATION_from_server_to_list

                print(f'Update messages in CONVERSATION: {convert_the_CONVERSATION_from_server_to_list}')
                return render_template('index.html', check_any_CONVERSATION_from_server=check_any_CONVERSATION_from_server)

            elif convert_the_list_to_string == '':
                print('No messages already in CONVERSATION from Server')
               
              

            else:
                print('ERROR !!! to get Update Message in CONVERSATION from SERVER')
        #############################################################
                        
        else:
             connection_status = 'Connection to Server is not successful !!!'
             print(connection_status)
             return render_template('index.html', connection_status=connection_status)
        
    except Exception as e:
        connection_status = 'NO Connection had Found !!!'
        print(connection_status, e)
        return render_template('index.html', connection_status=connection_status)

    
    return render_template('index.html', connection_status=connection_status, send_username_to_server=send_username_to_server)
    


@app.route('/get_message_from_client')
def get_message_from_client_and_send_to_server():
    global client_socket
    global CONVERSATION
  

    get_message = HTML_message
    if get_message != '':
        print(f'Display message From Flask: {username}: {get_message}')
        client_socket.sendall(get_message.encode())         # send message to server

        return redirect(url_for('get_CONVERSATION_from_server',send_username_to_server=send_username_to_server, connection_status=connection_status))
            
    else:
        print('message: ...')
        return redirect(url_for('get_dialog_from_server'))
    

@app.route('/get_CONVERSATION_from_server')
def get_CONVERSATION_from_server(): 
    global client_socket
    global send_username_to_server
    global connection_status
    global get_username
    global CONVERSATION # Here is Conversation is contain the messages from Server...
   
    
    get_username = send_username_to_server


    while True:
        get_message_from_server = client_socket.recv(2048).decode('utf-8') ### Get  the CONVERSATION from server by using Python-Sockets
        if get_message_from_server != '':
            

            CONVERSATION.append((get_message_from_server)) # Here is save the messages to CONVERSATION list
            print(f'Message from Server(Python-Sockets): {get_message_from_server}') #Print Conversation
            print(f'Add Messages to CONVERSTION list is successfully: {CONVERSATION}')
            return render_template('index.html', CONVERSATION=CONVERSATION, get_username=get_username, connection_status=connection_status)
           
        else:
            print('No Received any message empty conversation from the server')
        return render_template('index.html')




# Get data from Server.....############

@socketio.on('connection_status')
def handle_socketio_connection(connection_status_from_socketio):
    print('Connection Status From Socket.io:',connection_status_from_socketio)
    
@socketio.on('dialog')# get dialog from Serverhow can i
def handle_message(dialog):
    global get_dialog
    global live_CONVERSATON
    get_dialog = dialog
    if get_dialog:
        print('Received message from Socket.io:', get_dialog)
        live_CONVERSATON.append((get_dialog))
        emit('live_CONVERSATION', live_CONVERSATON, broadcast=True)
####################################################################
        
######### Get and send data from HTML page
    
@socketio.on('connect')
def send_data_to_html():
    global CONVERSATION
    if connection_status !='':
        emit('connection_status', connection_status, broadcast=True)
        emit('username', username,broadcast=True)
        emit('check_CONVERSATION', check_any_CONVERSATION_from_server, broadcast=True)

@socketio.on('send_message_from_html')
def get_message_from_html(message_from_html):
    global HTML_message
    HTML_message = message_from_html
    if HTML_message != '':
        print(f'MESSAGE FROM HTML: {HTML_message}')
        get_message_from_client_and_send_to_server()
   

    
if __name__ == '__main__':
    socketio.run(app, debug=True,host=MY_IP, port=5000)
