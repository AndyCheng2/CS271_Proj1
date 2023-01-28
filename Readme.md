# Totally Ordered Lamport Clock Project

## How to run this project
1. We should start server firstly with command `python server.py`
2. We need to run script `auto.py` that start three clients windows, I also provide the MacOS version
3. User interface
    ```python
    Hi, andy, please input what do you want to do
    1:Ask the balance of your account
    2 :Send money to someone
    3.Print blockchain queue
    4.Print your process_id
    0.Exit
    Input a number here:
    ```

## Blockchain Structure
In the block, I put some special elements to help me trace the information
```python
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
```

For the blockchain, I just use a list to store the block ,and only provide a `add_block` to allow user add blocks. `add_block`  traverse the list and find the right place to insert and re-computer the following hash
```python
class Blockchain:
    def __init__(self, chain=None):
        if chain is None:
            self.chain = [self.create_genesis_block()]
        else:
            self.chain = chain
    
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
```

## Project highlights
1. Store all information in local like `blockchain.json` and `balance.csv`, so when you logout you can also access to the previous data, if you want to initial all the information, just run `init.py`
2. Using the multi-threads to handle the user inputs and received messages, like message_queue, and mutex to handler data synchrinization
3. Providing as many functions as possible and use them to program sufficiently, like in blockchain, I provide `find_block()` , `find_first_pending_block()`, `print_chain()` , `find_block()`, to help me to code
4. Helpful script to handler the repetitive work, like `init.py` and `auto.py`

## Demo Bug fixed
When the demo time, there is a bug that when we get the first in queue and get other's reply, and when we do the transaction, sometimes(especially have many other messages) multi-thread will do the transaction twice, and it leading to a problem that balance table number is different from the blockchain log(in blockchain it only log transaction once).

I fixed this bug after the demo(don't have time in demo), it happens because when I tag the block as a success block, other threads, which is doing the detecting job like detecting if my sending request get other clients' reply, will all get into the transaction and do transactions twice even three times

I fixed it by changing the detecting condition, now it works smoothly