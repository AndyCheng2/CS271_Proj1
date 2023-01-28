import pandas as pd
import os

# Create a DataFrame with columns "name" and "amount"
data = {"name": ["andy", "bob", "cherry"], "amount": [10, 10, 10]}
df = pd.DataFrame(data)

# Write the DataFrame to a CSV file
df.to_csv('./data/balance.csv', index=False)

try:
    os.remove('./data/blockchain1.json')
    os.remove('./data/blockchain2.json')
    os.remove('./data/blockchain3.json')
except FileNotFoundError:
    print(f"Path does not exist")
