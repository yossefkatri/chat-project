import socket
import select
import msvcrt
import datetime

IP_SERVER = "127.0.0.1"
PORT_SERVER = 8080

message_to_send = []
user_name = ''


def prints(hour, username, content):
    print(hour+" " + username + ": " + content)


def get_response(data):
    if msvcrt.kbhit():
        ch = msvcrt.getch().decode()
        data += ch
        if ch == '\r':
            hour = datetime.datetime.now().strftime("%H:%M")
            prints(hour, user_name, data)
            return True, hour+data
    return False, data


def get_name():
    name = input("enter user-name:")
    return name


def get_pkt(msg):
    p = str(len(user_name)).zfill(4) + user_name + str(len(msg)).zfill(4) + msg
    return p.encode()


def print_pkt(data):# format: 0003 asd 0008 16:02 ffg
    user_len = int(data[:4])
    user = data[4:user_len+4]
    len = int(data[user_len+4:user_len + 8])
    msg = data[user_len + 8:user_len + 8 + len]
    hour = msg[:5]
    msg = msg[5:]
    prints(hour, user, msg)


def main():
    my_socket = socket.socket()
    my_socket.connect((IP_SERVER, PORT_SERVER))
    print(" welcome to the chat!!")
    global user_name
    user_name = get_name()
    msg = ''
    while True:
        rlist, wlist, xlist = select.select([my_socket], [my_socket], [])
        if my_socket in rlist:
            data = my_socket.recv(1024).decode()
            print_pkt(data)
        if my_socket in wlist:
            for msg1 in message_to_send:
                my_socket.send(get_pkt(msg1))
                message_to_send.remove(msg1)
        flag, data = get_response(msg)
        if flag:
            message_to_send.append(data)
            msg = ''
        else:
            msg = data
    my_socket.close()


if __name__ == '__main__':
    main()
