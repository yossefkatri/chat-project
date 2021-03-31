import socket
import select
import datetime
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


def exstract_msg(data):
    user_len = int(data[:4])
    user = data[4:user_len+4]
    len = int(data[user_len+4:user_len + 8])
    msg = data[user_len + 8:user_len + 8 + len]
    msg = msg[5:]
    return user, msg


def get_pkt(msg):
    msg = datetime.datetime.now().strftime("%H:%M ") + msg
    p = str(len(msg)).zfill(4) + msg
    return p


def main():
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', IP_SERVER))
    server_socket.listen(5)

    while True:
        rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
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
                    user, msg = exstract_msg(data)
                    if msg == "quit\r":
                        data = get_pkt(user+" has left the group")
                        open_client_sockets.remove(current_socket)
                        current_socket.close()
                        print("Connection with "+user+" closed")
                    send_to_sockets(current_socket, open_client_sockets, data)
        send_waiting_messages(wlist)


if __name__ == '__main__':
    main()