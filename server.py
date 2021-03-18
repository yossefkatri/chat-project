import socket
import select

IP_SERVER = 8080
open_client_sockets = []
messages_to_send = []


def send_to_sockets(except_socket, open_client_sockets, data):
    for current_socket in open_client_sockets:
        if current_socket != except_socket:
            messages_to_send.append((current_socket, data))


def send_waiting_messages(wlist):
    '''sends waiting messages that need to be sent, only if the client's socket is writeable'''
    for message in messages_to_send:
        client_socket, data = message
        if client_socket in wlist:
            client_socket.send(data.encode())
            messages_to_send.remove(message)


def main():
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', IP_SERVER))
    server_socket.listen(5)

    while True:
        rlist, wlist, xlist = select.select([server_socket] + open_client_sockets,open_client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                (new_socket, address) = server_socket.accept()
                open_client_sockets.append(new_socket)
                print("connection establish")
            else:
                data = current_socket.recv(1024).decode()
                if data == "":
                    open_client_sockets.remove(current_socket)
                    print("Connection with client closed")
                else:
                    #print(data)
                    send_to_sockets(current_socket, open_client_sockets, data)
        send_waiting_messages(wlist)


if __name__ == '__main__':
    main()