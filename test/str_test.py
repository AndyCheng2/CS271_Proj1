
message = "send andy cherry 1 1"

str_list = message.split()
request = str_list[0]
sender = str_list[1]
receiver = str_list[2]
amount = int(str_list[3])
clock = int(str_list[-1])
print(request)
print(sender)
print(receiver)
print(amount)
print(clock)