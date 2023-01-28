import socket
import threading
import pandas as pd
import time
import json
from blockchain import Blockchain, Block
from process_enum import Process_id

# another way is just use the broadcast and use the regulation to identify the reply

Balance_Path = './data/balance.csv'

clients = []


def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            client.send(message.encode())


def broadcast_all(message):
    for client in clients:
        client.send(message.encode())


# help the login function in client
def check_log(sender):
    df = pd.read_csv(Balance_Path)
    is_exist = df['name'].isin([sender]).any()
    if is_exist:
        # print("have")
        return True
    else:
        # print("none")
        return False


# check out the account balance
def check_amt(owner):
    df = pd.read_csv(Balance_Path)
    amount = str(df[df['name'] == owner]['amount'].values[0])
    return amount


# transaction
def change_amt(sender, receiver, amt):
    df = pd.read_csv(Balance_Path)
    # print(amt)
    df.loc[df['name'] == sender, 'amount'] -= amt
    df.loc[df['name'] == receiver, 'amount'] += amt
    df.to_csv(Balance_Path, index=False)

# def receive_client(client_socket, client_address):
#     while True:
#         try:
#             data = client_socket.recv(1024).decode()
#             handle_client_thread = threading.Thread(target=handle_client, args=(client_socket, data))
#             handle_client_thread.start()
#             handle_client_thread.join()
#         except ConnectionResetError:
#             print("Sever disconnected")
#             break
#     client_socket.close()
#     clients.remove(client_socket)


# A keep-on listening to handle all clients request
def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024).decode()
            message = data
            print("Received a message:" + message)
            str_list = message.split()
            request = str_list[0]
            sender = str_list[1]
            receiver = str_list[2]
            amount = int(str_list[3])
            tag_clock = int(str_list[-2])
            local_clock = int(str_list[-1])
            # print(request)
            # print(sender)
            # print(receiver)
            # print(amount)
            # print(tag_clock)
            # print(local_clock)
            if request == "login":
                if check_log(sender):
                    message = "server yes"
                    print("+++++++++++++++server: " + message)
                    client_socket.send(message.encode())
                else:
                    message = "server no"
                    print("+++++++++++++++server: " + message)
                    client_socket.send(message.encode())
            elif request == "balance":
                amount = check_amt(sender)
                message = "balance " + str(amount)
                print("+++++++++++++++server: " + message)
                client_socket.send(message.encode())
            elif request == "true":
                time.sleep(2)
                current_amt = int(check_amt(sender))
                if current_amt >= amount:
                    change_amt(sender, receiver, amount)
                    current_amt = int(check_amt(sender))
                    print("true send amount: " + str(amount))
                    message = "success " + sender + " " + str(current_amt) + " " + str(amount) + " " + str(
                        tag_clock) + " " + str(local_clock)
                    print("+++++++++++++++server broadcast: " + message)
                    broadcast_all(message)
                else:
                    message = "failed " + sender + " " + receiver + " " + str(amount) + " " + str(
                        tag_clock) + " " + str(local_clock)
                    print("+++++++++++++++server broadcast: " + message)
                    broadcast_all(message)
            elif request == "send":
                time.sleep(2)
                message = "send " + sender + " " + receiver + " " + str(amount) + " " + str(tag_clock) + " " + str(
                    local_clock)
                print("+++++++++++++++server broadcast: " + message)
                broadcast(message, client_socket)
            elif request == "reply":
                time.sleep(0.5)
                message = "reply " + sender + " " + receiver + " " + str(amount) + " " + str(tag_clock) + " " + str(
                    local_clock)
                print("+++++++++++++++server broadcast: " + message)
                broadcast(message, client_socket)
            elif request == "table":
                print("All user balances table:")
                df = pd.read_csv(Balance_Path)
                print(df)
            else:
                print("Bad request!")
                continue
    except:
        print("client TCP connect close")



def start_server(address, port):
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to a specific address and port
    server_socket.bind((address, port))
    # Listen for incoming connections
    server_socket.listen()
    print("Server is starting, listening for incoming connections...")
    while True:
        # Accept an incoming connection
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        client_handler = threading.Thread(target=handle_client, args=(client_socket, ))
        client_handler.start()
    # Close the server socket
    server_socket.close()


if __name__ == "__main__":
    start_server("localhost", 12349)
