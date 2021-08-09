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
            if data != "quit\r":
                prints(hour, user_name, data)
            return True, hour+data
    return False, data


def get_name():
    global user_name
    name = input("enter user-name:")
    p = str(len(name)).zfill(4)+name
    user_name = name
    return p.encode()


def get_pkt(msg, op): #support opcode 1,3
    if op == 1:
        p = str(len(user_name)).zfill(4) + user_name + str(op) + str(len(msg)).zfill(4) + msg
        return p.encode()
    elif op == 3:
        user = msg[10:]
        p = str(len(user_name)).zfill(4) + user_name + str(op) + str(len(user)).zfill(4) + user
        return p.encode()


def print_pkt(data):  # format: 0003 asd 0008 16:02 ffg
    user_len = int(data[:4])
    if user_len + 4 == len(data):  # server:0044 msg
        msg = data[4:user_len+4]
        print(msg)
    else:
        user = data[4:user_len+4]
        opcode = int(data[user_len+4:user_len+5])
        if opcode == 1:
            len1 = int(data[user_len+5:user_len + 9])
            msg = data[user_len + 9:user_len + 9 + len1]
            hour = msg[:5]
            msg = msg[5:]
            prints(hour, user, msg)


def main():
    my_socket = socket.socket()
    my_socket.connect((IP_SERVER, PORT_SERVER))
    print(" welcome to the chat!!")
    global user_name
    p = get_name()
    my_socket.send(p)
    msg = ''
    is_quit = True
    while is_quit:
        rlist, wlist, xlist = select.select([my_socket], [my_socket], [])
        if my_socket in rlist:
            data = my_socket.recv(1024).decode()
            if data == "":
                print("you have been kicked from the chat!")
                is_quit = False
                break
            print_pkt(data)
        if my_socket in wlist:
            for msg1 in message_to_send:
                opcode = 1
                if msg1[5:10] == "kick ":
                    opcode = 3
                my_socket.send(get_pkt(msg1, opcode))
                message_to_send.remove(msg1)
                if msg1[5:] == "quit\r":
                    is_quit = False
                    break
        flag, data = get_response(msg)
        if flag:
            message_to_send.append(data)
            msg = ''
        else:
            msg = data
    my_socket.close()


if __name__ == '__main__':
    main()
