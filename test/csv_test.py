import socket
import threading
import pandas as pd
Balance_Path = '../data/balance.csv'
import sys


def check_log(sender):
    df = pd.read_csv(Balance_Path)
    is_exist = df['name'].isin([sender]).any()
    if is_exist:
        print("have")
        return True
    else:
        print("none")
        return False


def check_amt(owner):
    df = pd.read_csv(Balance_Path)
    amount = str(df[df['name'] == owner]['amount'].values[0])
    return amount


def change_amt(sender, receiver, amt):
    df = pd.read_csv(Balance_Path)
    print(amt)
    df.loc[df['name'] == sender, 'amount'] -= amt
    df.loc[df['name'] == receiver, 'amount'] += amt
    df.to_csv(Balance_Path, index=False)


if __name__ == "__main__":
    name = "andy"
    s_name = "bob"
    while True:
        op = input("op:")
        print(op)
        if op == "1":
            print("+++++++++++++++")
            print("starting to check exist")
            if check_log(name):
                print("yes")
            else:
                print("no")
        elif op == "2":
            print("+++++++++++++++++")
            print("starting to check amount")
            print("Amount:" + check_amt(name))
        elif op == "3":
            print("+++++++++++")
            print("starting to change the amount")
            change_amt(name, s_name, 1)
            print("sender:" + check_amt(name))
            print("receiver:" + check_amt(s_name))
        elif op == "0":
            sys.exit()

        print("restart again!")

