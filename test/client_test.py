import queue
import sys, os
import socket
import time
import threading
from blockchain import Blockchain, Block
from process_enum import Process_id
from lamport_clock import Lamport_clock
import json

# q_lock here is just used to handle the access for the message_queue, do thread safe queue operations
message_queue = queue.Queue()
q_lock = threading.Lock()
login_state: bool = False
bc_state: bool = False
process_id = 0
name = "None"
tolc = Lamport_clock()
blockchain = Blockchain()
BC_PATH = '../data/blockchain.json'


def save_blockchain():
    with open(BC_PATH, "w") as f:
        f.write(json.dumps(blockchain.__dict__, default=lambda o: o.__dict__))


# Block: lamport_clock, process_id, transactions, pre_hash=None, tag="pending", index=10e5, cnt=0

def receive_socket(client_socket):
    global name, login_state, bc_state, process_id, tolc, blockchain, BC_PATH
    print("This client is listening")
    while True:
        # Receive messages from other clients
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                continue
            print("++++++++++++Get data from server: " + data)
            str_list = data.split()
            request = str_list[0]
            if request == "server":
                server_reply = str_list[-1]
                q_lock.acquire()
                message_queue.put(server_reply)
                q_lock.release()
            if login_state:
                if request == "balance":
                    server_balance = str_list[-1]
                    q_lock.acquire()
                    message_queue.put(server_balance)
                    q_lock.release()
                if bc_state:
                    if request == "success":
                        print("enter success")
                        sender = str_list[1]
                        proce_id = Process_id[sender].value
                        tag_clock = int(str_list[-2])
                        other_clock = int(str_list[-1])
                        success_block = blockchain.find_block(tag_clock, proce_id)
                        success_block.tag = "success"
                        success_block.cnt = 3
                        tolc.receive_event(other_clock)
                        if proce_id == process_id:
                            print("pass all test")
                            q_lock.acquire()
                            print("start request lock")
                            queue_message = "success"
                            message_queue.put(queue_message)
                            print("put success")
                            q_lock.release()
                            print("release lock")
                        save_blockchain()

                    elif request == "failed":
                        sender = str_list[1]
                        proce_id = Process_id[sender].value
                        tag_clock = int(str_list[-2])
                        other_clock = int(str_list[-1])
                        blockchain.find_block(tag_clock, proce_id).tag = "abort"
                        tolc.receive_event(other_clock)
                        if proce_id == process_id:
                            print("pass all test")
                            q_lock.acquire()
                            print("start request lock")
                            queue_message = "failed"
                            message_queue.put(queue_message)
                            print("put failed")
                            q_lock.release()
                            print("release lock")
                        save_blockchain()
                    elif request == "send":
                        sender = str_list[1]
                        receiver = str_list[2]
                        amount = str_list[3]
                        if sender != name:
                            proce_id = Process_id[sender].value
                            tag_clock = int(str_list[-2])
                            other_clock = int(str_list[-1])
                            tolc.receive_event(other_clock)
                            local_clock = tolc.get_time()
                            transactions = sender + " " + receiver + " " + amount
                            queue_block = Block(tag_clock, proce_id, transactions)
                            blockchain.add_block(queue_block)
                            message = "reply " + name + " " + sender + " " + amount + " " + str(tag_clock) + " " + str(local_clock)
                            client_socket.send(message.encode())
                        save_blockchain()
                    elif request == "reply":
                        reply_from = str_list[1]
                        reply_want = str_list[2]
                        reply_want_id = Process_id[reply_want].value
                        if reply_want_id == process_id:
                            print("here is reply_want id:" + str(reply_want_id))
                            tag_clock = int(str_list[-2])
                            other_clock = int(str_list[-1])
                            tolc.receive_event(other_clock)
                            local_clock = tolc.get_time()
                            reply_block = blockchain.find_block(tag_clock, reply_want_id)
                            reply_block.cnt += 1
                            print("reply_block transactions:" + reply_block.transactions)
                            if reply_block.cnt == 3 and reply_block == blockchain.find_first_pending_block():
                                tran_list = reply_block.transactions.split()
                                receiver = tran_list[-2]
                                amount = tran_list[-1]
                                message = "true " + name + " " + receiver + " " + str(amount) + " " + str(tag_clock) + " " + str(local_clock)
                                client_socket.send(message.encode())
                            save_blockchain()

            # q_lock.acquire()
            # message_queue.put(data)
            # q_lock.release()
        except ConnectionResetError:
            print("Sever disconnected")
            client_socket.close()
            break


def send_socket(client_socket):
    global name, login_state, bc_state, process_id, tolc, blockchain, BC_PATH
    # name = str(input("Please firstly input your username:")).lower()
    message = "login " + name + " none " + str(0) + " " + str(0)
    client_socket.send(message.encode())
    while True:
        q_lock.acquire()
        if not message_queue.empty():
            current_response = message_queue.get()
            message_queue.task_done()
            q_lock.release()
            print("+++++++++++++Starting to act follow the queue message:" + current_response)
            if current_response == "yes":
                login_state = True
                print("Login success " + name + " !")
                process_id = Process_id[name].value
                BC_PATH = '../data/blockchain{}.json'.format(process_id)
                print("process_id is: " + str(process_id))
                # print({BC_PATH})
                if os.path.exists(BC_PATH):
                    with open(BC_PATH, "r") as f:
                        blockchain_data = f.read()
                        blockchain_data = json.loads(blockchain_data)
                        # Block: lamport_clock, process_id, transactions, pre_hash=None, tag="pending", index=10e5,
                        # cnt=0
                        loaded_chain = [Block(block['tol_clock'][0], block['tol_clock'][-1], block['transactions'],
                                              block['pre_hash'], block['tag'], block['index'], block['cnt']) for block
                                        in blockchain_data["chain"]]
                        blockchain = Blockchain(chain=loaded_chain)
                        bc_state = True
                else:
                    blockchain = Blockchain()
                    save_blockchain()
                    bc_state = True
                tolc.set_time(blockchain.get_latest_block_time())
                while True:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("Hi, " + name + ", please input what do you want to do")
                    print("1:Ask the balance of your account")
                    print("2:Send money to someone")
                    print("3.Print blockchain queue")
                    print("0.Exit")
                    op = input("Input here:")
                    while not op.isdigit():
                        op = input("Input here:")
                    op = int(op)
                    if op == 1:
                        print("______________________op1")
                        local_clock = tolc.get_time()
                        message = "balance " + name + " none " + str(0) + " " + str(local_clock) + " " + str(local_clock)
                        client_socket.send(message.encode())
                        time.sleep(1)
                        q_lock.acquire()
                        print("lock get")
                        if not message_queue.empty():
                            response = message_queue.get()
                            print(name + ", Your balance is: " + str(response))
                            message_queue.task_done()
                            q_lock.release()
                            input("Press enter to continue")
                            continue
                        else:
                            print("Queue is still empty, please wait...")
                            input("Press enter to continue")
                            q_lock.release()
                            continue
                    elif op == 2:
                        print("__________________________op2")
                        receiver = str(input("Please input the username that you want to send: "))
                        amount = int(input("Please input the amount that you want to send: "))
                        tag_clock = tolc.send_event()
                        print("start to sending--" + str(tag_clock))
                        message = "send " + name + " " + receiver + " " + str(amount) + " " + str(tag_clock) + " " +str(tag_clock)
                        transactions = name + " " + receiver + " " + str(amount)
                        queue_block = Block(tag_clock, process_id, transactions)
                        queue_block.cnt += 1
                        blockchain.add_block(queue_block)
                        client_socket.send(message.encode())
                        save_blockchain()
                        time.sleep(3)
                        q_lock.acquire()
                        if not message_queue.empty():
                            response = message_queue.get()
                            if response == "success":
                                print(
                                    "Success! " + "Transaction: " + "send " + name + " " + receiver + " " + str(amount))
                                message_queue.task_done()
                                q_lock.release()
                                input("Press enter to continue")
                                continue
                            elif response == "failed":
                                print(
                                    "Failed! " + "Transaction: " + "send " + name + " " + receiver + " " + str(amount))
                                message_queue.task_done()
                                q_lock.release()
                                input("Press enter to continue")
                                continue
                        else:
                            print("Queue is still empty, please wait")
                            input("Press enter to continue")
                            continue
                    elif op == 3:
                        blockchain.print_chain()
                        input("Press enter to continue")
                        continue
                    elif op == 0:
                        sys.exit()
                        break
                    else:
                        print("Bad request, re-input again!")
                        input("Press enter to continue")
                        continue

            else:
                print("Don't find your username, please try again")
                input("Press enter to continue")
                continue
        else:
            q_lock.release()
            continue


if __name__ == "__main__":
    # Create a TCP socket
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = str(input("Please firstly input your username:")).lower()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    client_socket.connect(("localhost", 12345))
    # Start the send_message thread
    # Start the receive_messages thread
    send_thread = threading.Thread(target=send_socket, args=(client_socket,))
    send_thread.start()
    receive_thread = threading.Thread(target=receive_socket, args=(client_socket,))
    receive_thread.start()

