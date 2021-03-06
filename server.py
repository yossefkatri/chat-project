import socket
import select
import datetime

IP_SERVER = 8080
open_client_sockets = []
users = []
silence_users = []
messages_to_send = []
managers = []


def send_to_sockets(except_socket, open_client_sockets, data):
    """
    send to all sockets except the socket that is indicated
    :param except_socket: the socket that you should not to send
    :param open_client_sockets: the sockets list
    :param data: the message to be sent
    :return: none
    """
    for current_socket in open_client_sockets:
        if current_socket != except_socket:
            messages_to_send.append((current_socket, data))


def send_waiting_messages(wlist):
    """
    sends waiting messages that need to be sent, only if the client's socket is writeable
    :param wlist: the socket that can be wrote
    :return: none
    """
    for message in messages_to_send:
        client_socket, data = message
        if client_socket in wlist:
            client_socket.send(data.encode())
            messages_to_send.remove(message)


def exstract_msg(data):
    """
    exstract the info you need from the packet including opcode

    :param data: the packet

    :return: opcode, sender, more info depends on opcode

    """
    user_len = int(data[:4])
    sender = data[4:user_len + 4]
    opcode = int(data[user_len+4:user_len+5])
    if opcode == 1:
        len = int(data[user_len + 5:user_len + 9])
        msg = data[user_len + 9:user_len + 9 + len]
        return 1, sender, msg
    elif opcode == 2 or opcode == 4 or opcode == 6:
        len = int(data[user_len + 5:user_len + 9])
        user = data[user_len + 9:user_len + 9 + len]
        return opcode, sender, user
    elif opcode == 3:
        len = int(data[user_len + 5:user_len + 9])
        user = data[user_len + 9:user_len + 9 + len]
        return 3, sender, user
    elif opcode == 5:
        len = int(data[user_len + 5:user_len + 9])
        user = data[user_len + 9:user_len + 9 + len]
        len_msg = int(data[user_len + 9 + len:user_len + 13 + len])
        msg = data[user_len + 13 + len:user_len + 13 + len + len_msg]
        return 5, sender, (user, msg)
    elif opcode == 7:
        return 7, sender, None


def get_pkt(msg):
    """
    make a server message that will send everyone.
    :param msg: the message
    :return: the packet that should be sent
    """
    msg = datetime.datetime.now().strftime("%H:%M ") + msg
    p = str(len(msg)).zfill(4) + msg
    return p


def get_socket(current_user):
    """
    get socket from user name
    :param current_user: user name
    :return: correspond socket and true or false if exists one
    """
    for user in users:
        name, socket = user
        if name == current_user:
            return socket, True
    return False, False


def get_user(current_socket):
    """
    get user name from socket
    :param current_socket: socket
    :return: correspond user name and true or false if exists one
    """
    for user in users:
        name, socket = user
        if socket == current_socket:
            return name, True
    return False, False


def quit_user(current_socket, user, op):
    """
    the function kick the user from the chat depends on opcode.

    :param current_socket: the socket of the user to be kicked
    :param user: the user name to be kicked
    :param op: opcode
    :return: the message that the server should send
    """
    if user in managers:
        managers.remove(user)
    if op == 1:
        data = get_pkt(user + " has left the chat!")
        open_client_sockets.remove(current_socket)
        users.remove((user, current_socket))
        current_socket.close()
        print("Connection with " + user + " closed")
        return data
    elif op == 3:
        data = get_pkt(user + " has been kicked from the chat!")
        open_client_sockets.remove(current_socket)
        users.remove((user, current_socket))
        current_socket.close()
        print("Connection with " + user + " closed")
        return data


def only_user(data):
    """
    check if the message is contained only the name of the user
    :param data: the message
    :return: true or false
    """
    user_len = int(data[:4])
    return user_len + 4 == len(data)


def exstract_user(data):
    """
    exstract the user name from the msg
    :param data: packet that be sent
    :return: the user name who sent it
    """
    user_len = int(data[:4])
    return data[4:user_len + 4]


def get_regular_msg(sender, msg):
    """
        turn uniqe msg to regular one

        :param sender: the sender message
        :param msg: the user he try yo kick
        :param hour: the clock
        :return: the encoded regular message
        """
    time = datetime.datetime.now().strftime("%H:%M")
    msg = time + "kick " + msg
    p = str(len(sender)).zfill(4) + sender + str(1) + str(len(msg)).zfill(4) + msg
    return p


def mannger_msg(mannger, msg, time):
    """
    put into the user name the '@' character.
    :param mannger: the sender name
    :param msg: the msg he try to send
    :return: the packet to be sended
    """
    user = "@" + mannger
    msg = time + msg
    p = str(len(user)).zfill(4) + user + str(1) + str(len(msg)).zfill(4) + msg
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
                try:
                    data = current_socket.recv(1024).decode()
                except:
                    data = ""
                if data == "":  # close the connection with the socket
                    open_client_sockets.remove(current_socket)
                    user, ok = get_user(current_socket)
                    if ok:  # we found the socket
                        users.remove((user, current_socket))
                        if user in managers:
                            managers.remove(user)
                        data = get_pkt(user + " has left the chat!")
                        send_to_sockets(current_socket, open_client_sockets, data)
                        print("Connection with " + user + " closed")
                elif only_user(data):  # format:0004asdf, to match between user and socket
                    user = exstract_user(data)
                    if not managers:
                        managers.append(user)
                    users.append((user, current_socket))
                else:
                    send_flag = True
                    opcode, user, msg = exstract_msg(data)
                    if opcode == 1:   # if user wants to quit
                        if msg[5:] == "quit\r":
                            data = quit_user(current_socket, user, opcode)
                    if opcode == 1 and user in managers:  # should insert '@' before the name
                        time = msg[:5]
                        data = mannger_msg(user, msg[5:], time)
                    elif opcode == 2 and user in managers:  # if manager wants to ordain someone to be a manager
                        soc, check = get_socket(msg)  # msg == user he wants to ordain is real.
                        if check and user != msg:
                            managers.append(msg)
                            data = get_pkt(msg + " become a manager!!!")
                            current_socket = -1  # send to everyone
                        else:
                            send_flag = False
                            messages_to_send.append((current_socket, get_pkt("The server can't find the user or the user is you")))
                    elif opcode == 3:
                        msg = msg[:-1]
                        soc, check = get_socket(msg)  # msg == user he wants to kick is real.
                        if user in managers and check and user != msg:
                            data = quit_user(soc, msg, opcode)  # kick the user
                            current_socket = -1  # send to everyone
                        else:
                            data = get_regular_msg(user, msg)
                    elif opcode == 4 and user in managers:  # if manager try to silence a user.
                        soc, check = get_socket(msg)  # msg == user he wants to silence is real.
                        if check:
                            silence_users.append(msg)
                            data = get_pkt(msg + " is silenced by "+user)
                            current_socket = -1  # send to everyone
                        else:
                            send_flag = False
                            messages_to_send.append((current_socket, get_pkt("The server can't find the user")))
                    elif opcode == 6 and user in managers:  # if manager try to un-silence a user.
                        soc, check = get_socket(msg)  # msg == user he wants to un-silence is real.
                        if check and msg in silence_users:  # if the user exists and the user was silenced
                            silence_users.remove(msg)
                            data = get_pkt(msg + " is un-silenced by "+user)
                            current_socket = -1  # send to everyone
                        else:
                            send_flag = False
                            messages_to_send.append((current_socket, get_pkt("The server can't find the user or the user isn't silenced")))
                    if opcode == 7:
                        msg = "managers: "+", ".join(managers)
                        messages_to_send.append((current_socket, get_pkt(msg)))
                    elif opcode == 5:  # if user wants to send a private message
                        rec, msg = msg
                        soc, check = get_socket(rec)  # if the user is real.
                        if check:
                            messages_to_send.append((soc, data))
                        else:
                            messages_to_send.append((current_socket, get_pkt("the server can't find the user")))
                    elif user not in silence_users or opcode != 1 or (msg[5:] == "quit\r" and opcode == 1):
                        if send_flag:
                            send_to_sockets(current_socket, open_client_sockets, data)
                    else:
                        messages_to_send.append((current_socket, get_pkt("You can't speak here")))
        send_waiting_messages(wlist)


if __name__ == '__main__':
    main()
