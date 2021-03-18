import socket
import select
import msvcrt

IP_SERVER = "127.0.0.1"
PORT_SERVER = 8080

message_to_send = []
user_name = ''

def prints(username, content):
    print(username+": "+content)


def get_response(data):
    if msvcrt.kbhit():
        ch = msvcrt.getch().decode()
        msvcrt.putch(ch.encode())
        data += ch
        if ch == '\r':
            print()
            return True, data
    return False, data

#TODO get name MAX 4 charcters
def get_name():
    name = input("enter user-name:")
    return name


def get_pkt(msg):
    p = str(len(user_name)).zfill(4) + user_name + str(len(msg)) + msg
    return p.encode()

#TODO extract the data and print 'user: msg'
def print_pkt(data):
    pass


def main():
    my_socket = socket.socket()
    my_socket.connect((IP_SERVER, PORT_SERVER))
    print(" welcome to the chat!!")
    user_name = get_name()
    print(user_name, end=':')
    msg = ''
    while True:
        rlist, wlist, xlist = select.select([my_socket], [my_socket], [])
        if my_socket in rlist:
            data = my_socket.recv(1024).decode()
            print_pkt(data)
        if my_socket in wlist:
            for msg in message_to_send:
                my_socket.send(get_pkt(msg))
                message_to_send.remove(msg)
        flag, data = get_response(msg)
        if flag:
            message_to_send.append(data)
            msg = ''
            print(user_name, end=':')
        else:
            msg = data
    my_socket.close()


if __name__ == '__main__':
    main()