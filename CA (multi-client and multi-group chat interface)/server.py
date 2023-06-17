import threading
import socket

# Define the host and port
HOST = '127.0.0.1'
PORT = 59000

# Define the User class
class User:
    def __init__(self, client_socket, alias):
        self.client_socket = client_socket
        self.alias = alias

# Define the Group class
class Group:
    def __init__(self, name):
        self.name = name
        self.users = []

# Create the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

# Define a list of groups
GROUPS = []
USERS = []

# Define the broadcast function
def broadcast(user, message):
    for client in USERS:
        client.client_socket.sendall(f'[broadcast@{user.alias}] {message}'.encode())

def publicMessage(user,groupName,message):
    found = False
    for group in GROUPS:
        if group.name == groupName:
            found = True
            if user in group.users:
                for client in group.users:
                    if client is not user.client_socket:
                        client.client_socket.sendall(f'[{user.alias}@{group.name}] {message}'.encode())
            else:
                user.client_socket.sendall(f'You are not a member of group {groupName}'.encode())
    if not found:
        user.client_socket.sendall(f'Group Not Found!'.encode())

def privateMessage(user,clientName,message):
    found = False
    for client in USERS:
        if client.alias == clientName:
            found = True
            client.client_socket.sendall(f'[private@{user.alias}] {message}'.encode())
    if not found:
        user.client_socket.sendall(f'Client Not Found!'.encode())
        



# Define the function to handle clients' connections
def handle_client(user):
    while True:
        try:
            message = user.client_socket.recv(1024)
            words = message.decode().split(" ")
            if words[0] == 'groups':
                group_names = '\n'.join([group.name for group in GROUPS])
                user.client_socket.sendall(f'Available groups: \n{group_names}'.encode())

            elif words[0] == 'users':
                user_names = '\n'.join([user.alias for user in USERS])
                user.client_socket.sendall(f'Online users: \n{user_names}'.encode())

            elif words[0] == 'create':
                found = False
                for group in GROUPS:
                    if group.name == words[1]:
                        user.client_socket.sendall(f'Group already exists!'.encode())
                        found = True
                if not found:
                    g = Group(message.decode().split(" ")[1])
                    GROUPS.append(g)
                    user.client_socket.sendall(f'New group {g.name} Created'.encode())
            

            elif words[0] == 'leave':
                found = False
                for group in GROUPS:
                    if group.name == words[1]:
                        found = True
                        if user in group.users:
                            publicMessage(user, group.name , f'{user.alias} jsut left {group.name} group!')
                            group.users.remove(user)
                            user.client_socket.sendall(f'You left the group {group.name}'.encode())
                        else:
                            user.client_socket.sendall(f'You are not a member of group {group.name}'.encode())
                if not found:
                    user.client_socket.sendall(f'Group Not Found!'.encode())


            elif words[0] == 'join':
                found = False
                for group in GROUPS:
                    if group.name == words[1]:
                        found = True
                        if user not in group.users:
                            group.users.append(user)
                            user.client_socket.sendall(f'You joined group {group.name}'.encode())
                            publicMessage(user, group.name , f'{user.alias} has joined the {group.name} group!')
                        else:
                            user.client_socket.sendall(f'You already joined group {group.name}'.encode())
                if not found:
                    user.client_socket.sendall(f'Group Not Found!'.encode())

            elif words[0] == 'public':
                publicMessage(user, words[1], ' '.join(words[2:]))

            elif words[0] == 'private':
                privateMessage(user, words[1], ' '.join(words[2:]))
            
            elif words[0] == 'broadcast':
                broadcast(user, ' '.join(words[1:]))

            elif words[0] == 'exit':
                for group in GROUPS:
                    if user in group.users:
                        publicMessage(user, group.name , f'{user.alias} jsut left {group.name} group!')
                        group.users.remove(user)
                        alias = user.alias
                USERS.remove(user)
                print(f'user {user.alias} got disconnected...')
                user.client_socket.close()


            






            else:
                for group in GROUPS:
                    if user in group.users:
                        broadcast(user, message.decode())
                        break
        except:
            for group in GROUPS:
                if user in group.users:
                    group.users.remove(user)
                    alias = user.alias
                    broadcast(user, f'{alias} has left the {group.name} group!'.encode())
                    break
            user.client_socket.close()
            break

# Define the main function to receive clients' connections
def receive():
    while True:
        print('Server is running and listening ...')
        client_socket, address = server_socket.accept()
        print(f'connection is established with {str(address)}')

        # Get the alias from the client
        client_socket.sendall('alias?'.encode('utf-8'))
        alias = client_socket.recv(1024).decode()

        # Create a new User object
        user = User(client_socket, alias)
        USERS.append(user)

        # Send a message to the user indicating that they have connected
        client_socket.sendall('you are now connected! \n'.encode('utf-8'))

        group = GROUPS[0]
        group.users.append(user)
        client_socket.sendall(f'you are joined in group {group.name} \n'.encode('utf-8'))

        # Broadcast a message to all clients that a new user has joined
        print(f'The alias of this client is {alias}'.encode('utf-8'))

        publicMessage(user,group.name, f'{alias} has joined the {group.name} group!')

        # Start a new thread to handle the client
        thread = threading.Thread(target=handle_client, args=(user,))
        thread.start()


def createGroup(name):
    g = Group(name)
    GROUPS.append(g)
    

if __name__ == "__main__":
    createGroup("General")  
    receive()