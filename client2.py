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
BC_PATH = './dtat/blockchain.json'


def save_blockchain():
    with open(BC_PATH, "w") as f:
        f.write(json.dumps(blockchain.__dict__, default=lambda o: o.__dict__))


# Block: lamport_clock, process_id, transactions, pre_hash=None, tag="pending", index=10e5, cnt=0

def receive_socket(client_socket, data):
    global name, login_state, bc_state, process_id, tolc, blockchain, BC_PATH
    print("---------------------------Get data from server: " + data)
    str_list = data.split()
    request = str_list[0]
    if request == "server":
        server_reply = str_list[-1]
        with q_lock:
            message_queue.put(server_reply)
    if request == "balance":
        server_balance = str_list[-1]
        print("Your balance now is: " + str(server_balance))
    if bc_state:
        if request == "success":
            sender = str_list[1]
            proce_id = Process_id[sender].value

            tag_clock = int(str_list[-2])
            other_clock = int(str_list[-1])
            success_block = blockchain.find_block(tag_clock, proce_id)
            if success_block.tag == "success":
                return
            success_block.tag = "success"
            with q_lock:
                success_block.cnt = 4
            tolc.receive_event(other_clock)
            print("Now clock: ", str(tolc.get_time()))
            print("tag a success block: " + success_block.transactions)
            if proce_id == process_id:
                current_amount = int(str_list[2])
                print("\nSuccess! Transaction is (" + success_block.transactions + ")\n")
                print("Your current balance is:"+ str(current_amount) + "\n")
            save_blockchain()
            return
        elif request == "failed":
            sender = str_list[1]
            proce_id = Process_id[sender].value
            tag_clock = int(str_list[-2])
            other_clock = int(str_list[-1])
            fail_block = blockchain.find_block(tag_clock, proce_id)
            fail_block.tag = "abort"
            tolc.receive_event(other_clock)
            print("Now clock: ", str(tolc.get_time()))
            if proce_id == process_id:
                print("Failed! Transaction is: " + fail_block.transactions)
            local_clock = tolc.get_time()
            message = "balance " + name + " none " + str(0) + " " + str(local_clock) + " " + str(local_clock)
            client_socket.send(message.encode())
            save_blockchain()
        elif request == "send":
            print("receive other send request")
            sender = str_list[1]
            receiver = str_list[2]
            amount = str_list[3]
            proce_id = Process_id[sender].value
            tag_clock = int(str_list[-2])
            other_clock = int(str_list[-1])
            tolc.receive_event(other_clock)
            print("Now clock: ", str(tolc.get_time()))
            local_clock = tolc.get_time()
            transactions = sender + " " + receiver + " " + amount
            queue_block = Block(tag_clock, proce_id, transactions)
            blockchain.add_block(queue_block)
            message = "reply " + name + " " + sender + " " + amount + " " + str(tag_clock) + " " + str(local_clock)
            print("send reply finsh")
            client_socket.send(message.encode())
            save_blockchain()
        elif request == "reply":
            reply_from = str_list[1]
            reply_want = str_list[2]
            reply_want_id = Process_id[reply_want].value
            if reply_want_id == process_id:
                # print("here is reply_want id:" + str(reply_want_id))
                tag_clock = int(str_list[-2])
                other_clock = int(str_list[-1])
                tolc.receive_event(other_clock)
                local_clock = tolc.get_time()
                print("Now clock: ", str(tolc.get_time()))
                reply_block = blockchain.find_block(tag_clock, reply_want_id)
                with q_lock:
                    reply_block.cnt += 1
                print("reply_block transactions:" + reply_block.transactions)
                print("reply block cnt: " + str(reply_block.cnt))
                save_blockchain()
                if reply_block.cnt == 3:
                    while True:
                        time.sleep(2)
                        print("wait in while")
                        blockchain.print_chain()
                        if reply_block == blockchain.find_first_pending_block():
                            print("into if")
                            tran_list = reply_block.transactions.split()
                            receiver = tran_list[-2]
                            amount = tran_list[-1]
                            print("send sever transaction execute")
                            message = "true " + name + " " + receiver + " " + str(amount) + " " + str(tag_clock) + " " + str(local_clock)
                            client_socket.send(message.encode())
                            return

                        else:
                            continue

                else:
                    print("exit the thread")
                    return
    print("exit the thread")
    return





def send_socket(client_socket):
    global name, login_state, bc_state, process_id, tolc, blockchain, BC_PATH
    login_state = True
    print("Login success " + name + " !")
    BC_PATH = './data/blockchain{}.json'.format(process_id)
    print("process_id is: " + str(process_id))
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
        print("4.Print your process_id")
        print("0.Exit")
        op = input("Input a number here:")
        while not op.isdigit():
            op = input("Input here:")
        op = int(op)
        if op == 1:
            print("______________________op1")
            local_clock = tolc.get_time()
            message = "balance " + name + " none " + str(0) + " " + str(local_clock) + " " + str(local_clock)
            client_socket.send(message.encode())
            print("Please wait...")
            input("Press enter to continue")
        elif op == 2:
            print("__________________________op2")
            receiver = str(input("Please input the username that you want to send: "))
            while receiver == name or (receiver != "andy" and receiver != "bob" and receiver != "cherry"):
                receiver = input("Please input the correct name:  ")
            amount = input("Please input the amount that you want to send: ")
            while not amount.isdigit():
                amount = input("Please input a number:")
            amount = int(amount)
            tag_clock = tolc.send_event()
            print("get the local clock " + str(tag_clock) + ", please wait for 3 sec")
            message = "balance " + name + " none " + str(0) + " " + str(tolc.get_time()) + " " + str(tolc.get_time())
            client_socket.send(message.encode())
            time.sleep(3)
            print("start to sending -- at clock " + str(tag_clock))
            message = "send " + name + " " + receiver + " " + str(amount) + " " + str(tag_clock) + " " +str(tag_clock)
            transactions = name + " " + receiver + " " + str(amount)
            queue_block = Block(tag_clock, process_id, transactions)
            queue_block.cnt += 1
            blockchain.add_block(queue_block)
            client_socket.send(message.encode())
            save_blockchain()
            print("Please wait...")
            input("Press enter to continue")
            continue
        elif op == 3:
            print("__________________________op3")
            blockchain.print_chain()
            input("Press enter to continue")
            continue
        elif op == 4:
            print("__________________________op4")
            print("Your process_id is: " + str(process_id))
            input("Press enter to continue")
            continue
        elif op == 5:
            message = "table " + name + " none " + str(0) + " " + str(tolc.get_time()) + " " + str(tolc.get_time())
            client_socket.send(message.encode())
        elif op == 0:
            sys.exit()
            break
        else:
            print("Bad request, re-input again!")
            input("Press enter to continue")
            continue



if __name__ == "__main__":
    # Create a TCP socket
    if len(sys.argv) > 1:
        name = sys.argv[1]
        process_id = Process_id[name].value
    else:
        name = str(input("Please firstly input your username:")).lower()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 12347))
    send_thread = threading.Thread(target=send_socket, args=(client_socket,))
    send_thread.start()

    while True:
        data = client_socket.recv(1024).decode()
        # print("new thread created, message is: " + data)
        receive_thread = threading.Thread(target=receive_socket, args=(client_socket, data))
        receive_thread.start()
        # receive_thread.join()
        print("one thread close")

