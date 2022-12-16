"""
Authors: Ajinkya Vijay Sonawane, Sidharth Purohit
Python script to generate Load.sql file to insert data into our database
"""

import string
import random
from random import randint
from datetime import datetime

def rand_x_digit_num(x, leading_zeroes=True):
    """Return an X digit number, leading_zeroes returns a string, otherwise int"""
    if not leading_zeroes:
        # wrap with str() for uniform results
        return random.randint(10**(x-1), 10**x-1)  
    else:
        if x > 6000:
            return ''.join([str(random.randint(0, 9)) for i in xrange(x)])
        else:
            return '{0:0{x}d}'.format(random.randint(0, 10**x-1), x=x)


user_ids = []
token_ids = set()
url = "nft.io/"
nft_names = []
audit_path = "Audit/"
first_names = []
last_names = []

with open("data/names_nft.txt") as file:
    nft_names = file.readlines()
with open("data/names_first.txt","r") as f:
    first_names = f.readlines()                
with open("data/names_last.txt","r") as f:
    last_names = f.readlines()

fl = len(first_names)-1
ll = len(last_names)-1
load_sql_file_path = "scripts/load.sql"
with open(load_sql_file_path,"w+") as file:
    for i in range(30):
        f = first_names[randint(0,fl)][:-2]        
        temp = f + " " + last_names[randint(0,ll)][:-2]
        id = f.lower()+str(datetime.timestamp(datetime.now()))
        user_ids.append(id)
        # names.append(temp)
        file.write("INSERT INTO Account (user_id, name, age) VALUES ('"+id+"', '"+temp+"','"+str(randint(18,30))+"');\n")
        audit_id = str(datetime.timestamp(datetime.now()))
        file.write("INSERT INTO Audit (audit_id,audit_description, audit_path, audit_timestamp)"+
        " VALUES ('"+audit_id+"','Account Created', '"+audit_path+"_Account_Log',now());\n")
        file.write("INSERT INTO Account_Log (audit_id,user_id)"+
        " VALUES ('"+audit_id+"','"+id+"');\n")
    file.write("\n")

with open(load_sql_file_path,"a") as file:
    for user_id in user_ids:
        file.write("INSERT INTO Login_requires (login_id, password, security_question, security_answer, user_id) VALUES ('"+user_id+"', 'password123','What is the name of your pet?','Tom','"+user_id+"');\n")
        audit_id = str(datetime.timestamp(datetime.now()))
        file.write("INSERT INTO Audit (audit_id,audit_description, audit_path, audit_timestamp)"+
        " VALUES ('"+audit_id+"','Login Created', '"+audit_path+"_Login_Log',now());\n")
        file.write("INSERT INTO Login_Log (audit_id,login_id)"+
        " VALUES ('"+audit_id+"','"+user_id+"');\n")
    file.write("\n")

with open(load_sql_file_path,"a") as file:        
    for i in range(50):
        token_id = ''.join(random.choices(string.ascii_letters, k=16))
        while(token_id in token_ids):
            token_id = ''.join(random.choices(string.ascii_letters, k=16))                
        nl = len(nft_names)-1
        token_ids.add(token_id)
        file.write("INSERT INTO NFT (token_id,token_name,nft_url,current_value) VALUES ('"+token_id+"','"+nft_names[randint(0,nl)]+"','"+url+token_id+"',"+str(randint(1,100))+");\n")
        audit_id = str(datetime.timestamp(datetime.now()))
        file.write("INSERT INTO Audit (audit_id,audit_description, audit_path, audit_timestamp)"+
        " VALUES ('"+audit_id+"','NFT Created', '"+audit_path+"_NFT_Log',now());\n")
        file.write("INSERT INTO NFT_Log (audit_id,token_id)"+
        " VALUES ('"+audit_id+"','"+token_id+"');\n")
    file.write("\n")

with open(load_sql_file_path,"a") as file:
    ul = len(user_ids) - 1
    for token_id in list(token_ids):
        file.write("INSERT INTO NFT_created (token_id,user_id) VALUES ('"+token_id+"','"+user_ids[randint(0,ul)]+"');\n")
    file.write("\n")

with open(load_sql_file_path,"a") as file:
    ul = len(user_ids) - 1
    for token_id in list(token_ids):
        file.write("INSERT INTO NFT_owned (token_id,user_id) VALUES ('"+token_id+"','"+user_ids[randint(0,ul)]+"');\n")
    file.write("\n")

with open(load_sql_file_path,"a") as file:
    banks = ["Bank Of America","JPM Chase","Wells Fargo","Capital One","Santander Bank"]
    currencies = ["ETH","BTC","XRP","AST","MAT"]
    wallet_ids = []
    for user_id in user_ids:
        file.write("INSERT INTO Financial_Information_contains"+ 
        " (fin_id, card_number,card_cvv,bank_name,expiry_month,expiry_year,user_id)"+ 
        " VALUES ('"+str(datetime.timestamp(datetime.now()))+"',"+str(rand_x_digit_num(12))+","+str(rand_x_digit_num(3))+",'"+banks[randint(0,4)]+"',"+str(randint(1,12))+","+str(randint(2022,2030))+",'"+user_id+"');\n")
        wallet_id = str(datetime.timestamp(datetime.now()))
        file.write("INSERT INTO Wallet_has (wallet_id,wallet_address,user_id) VALUES ('"+wallet_id+"','0x"+rand_x_digit_num(16)+"','"+user_id+"');\n")
        wallet_ids.append(wallet_id)
    for wallet_id in wallet_ids:
        file.write("INSERT INTO Currency_holds (currency_name, balance, wallet_id) VALUES ('"+currencies[randint(0,4)]+"',"+str(randint(1,100))+",'"+wallet_id+"');\n")
    file.write("\n")

with open(load_sql_file_path,"a") as file:
    ul = len(user_ids)-1
    for token_id in list(token_ids):
        txn_id = str(datetime.timestamp(datetime.now()))        
        user_id = user_ids[randint(0,ul)]
        file.write("INSERT INTO Transactions_contains" + 
        " (txn_id, amount, status, token_id) VALUES "+
        "('"+txn_id+"',"+str(randint(1,100))+",True,'"+token_id+"');\n")
        file.write("INSERT INTO Buy_TXN" + 
        " (txn_id, user_id) VALUES "+
        "('"+txn_id+"','"+user_id+"');")
        file.write("INSERT INTO Sell_TXN" + 
        " (txn_id, user_id) VALUES "+
        "('"+txn_id+"',"+
        "(SELECT user_id FROM NFT_owned where token_id = '"+token_id+"'));\n")
        file.write("UPDATE NFT_owned SET user_id = '"+user_id+"' WHERE token_id = '"+token_id+"';\n"); 
    file.write("\n")