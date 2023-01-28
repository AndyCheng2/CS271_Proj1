from blockchain import Blockchain, Block
import json


bc = Blockchain()
print("++++++++++")
print(bc.chain)
print("-----------------------")
bc.print_chain()
print(bc.chain[0].tol_clock)
print("++++++++++++++++++++")
print("pass bc print_chain")
# Block: lamport_clock, process_id, transactions, pre_hash=None, tag="pending", index=10e5, cnt=0
block = Block(1,1,"send andy cherry 1")
print("start print new block++++++++++")
print(block)
print(block.tol_clock)

print("start to add and print chain")
bc.add_block(block)
print("add finish")
bc.print_chain()
print("--------------------")

print("add block2 and block3")
block2 = Block(6,3,"send cherry andy 1")
block3 = Block(4,2,"send bob cherry 1")
block4 = Block(4,1,"send andy bob 1")

bc.add_block(block2)
bc.add_block(block3)
bc.add_block(block4)
print("add finish start print")
bc.print_chain()
print(bc.get_latest_block_time())
print("***********************")
find_block = bc.find_first_pending_block()
print(find_block)
if find_block is None:
    print("None")
else:
    print("Block")
    find_block.cnt += 1
    print("<"+find_block.transactions +"> "+ str(find_block.cnt))



blockchain_data = json.dumps(bc.__dict__, default=lambda o: o.__dict__)
with open("../data/blockchain.json", "w") as f:
    f.write(blockchain_data)

with open("../data/blockchain.json", "r") as f:
    blockchain_data = f.read()

blockchain_data = json.loads(blockchain_data)
# Block: lamport_clock, process_id, transactions, pre_hash=None, tag="pending", index=10e5, cnt=0
loaded_chain = [Block(block['tol_clock'][0], block['tol_clock'][-1], block['transactions'], block['pre_hash'], block['tag'], block['index'], block['cnt']) for block in blockchain_data["chain"]]
blockchain = Blockchain(chain=loaded_chain)

print("start blockchain")
print(blockchain.chain)
print("end blockchain")
print("\n\n")
blockchain.print_chain()
print("pass blockchain print")


