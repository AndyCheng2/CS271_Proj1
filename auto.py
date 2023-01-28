import os
import time

# auto.py used to run three client with typical account name and I also add the MacOS version used to test
# provide the initial methods init.py

os.system('start cmd /C "python init.py"')
time.sleep(1)
os.system('start cmd /K "python client2.py andy"')
os.system('start cmd /K "python client2.py bob"')
os.system('start cmd /K "python client2.py cherry"')



# Above is MacOS version


# import os
# import time
# os.system('python init.py &')
# time.sleep(1)
# os.system('python client2.py andy &')
# os.system('python client2.py bob &')
# os.system('python client2.py cherry &')
