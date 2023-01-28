import hashlib
import json
import operator
from threading import Lock
import os

lock = Lock()


class Block:
    def __init__(self, lamport_clock, process_id, transactions, pre_hash=None, tag="pending", index=10e5, cnt=0):
        self.tol_clock = (lamport_clock, process_id)
        self.transactions = transactions
        self.pre_hash = pre_hash
        self.tag = tag
        self.process_id = process_id
        self.index = index
        self.cnt: int = cnt
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            'index': self.index,
            'tol_clock': self.tol_clock,
            'transaction': self.transactions,
            'pre_hash': self.pre_hash,
        }
        block_data_str = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_data_str).hexdigest()


class Blockchain:
    def __init__(self, chain=None):
        if chain is None:
            self.chain = [self.create_genesis_block()]
        else:
            self.chain = chain

    def find_block(self, lamport_clock, process_id):
        tolc_tuple = (lamport_clock, process_id)
        for block in self.chain:
            if operator.eq(tolc_tuple, block.tol_clock):
                return block
        return None

    def add_block(self, new_block):
        with lock:
            for i in range(len(self.chain)):
                if operator.gt(new_block.tol_clock, self.chain[i].tol_clock):
                    self.chain.insert(i, new_block)
                    new_block.index = i
                    new_block.pre_hash = self.chain[i - 1].hash
                    new_block.hash = new_block.calculate_hash()
                    if i == len(self.chain):
                        break
                    else:
                        start_index = i + 1
                        for j in range(start_index, len(self.chain)):
                            self.chain[j].pre_hash = self.chain[j - 1].hash
                            self.chain[j].hash = self.chain[j].calculate_hash()
                        break

    @staticmethod
    def create_genesis_block():
        # Block: lamport_clock, process_id, transactions, pre_hash=None, tag="pending", index=10e5, cnt=0
        return Block(0, 0, "0", "0", "success", 0, 3)

    def get_latest_block_time(self):
        with lock:
            return int(self.chain[0].tol_clock[0])

    def print_chain(self):
        current_block = self.chain[0]
        for i in range(1, len(self.chain)):
            # current_state ="NO." + str(i) + current_block.transactions + " " + current_block.tag
            current_state = "<" + current_block.transactions + "> " + str(current_block.tol_clock) + " " + current_block.tag
            print(current_state, "---->", end=" ")
            current_block = self.chain[i]
        print(current_block.transactions + " " + current_block.tag + "\n")

    def find_first_pending_block(self):
        for f_block in reversed(self.chain):
            if f_block.tag == "pending":
                return f_block
        return None


