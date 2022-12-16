import psycopg2
import pandas as pd
import streamlit as st
from datetime import datetime
from configparser import ConfigParser

"# NFT Marketplace Data"
"### CS-GY 6083: Principals of Database Systems"
"#### Contributors: avs8687 & sp6365"

@st.cache
def get_config(filename="config/database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

def query_db(query):
    try:
        db_info = get_config()
        conn = psycopg2.connect(**db_info)        
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        return pd.DataFrame(data=data, columns=column_names)
    except Exception as ex:
        print(ex)
        st.write("Sorry! Something went wrong with this query, please try again.")


def transact(buyer, seller, nft, amount):
    nft_query = """
    UPDATE nft SET current_value = %s where token_id = %s;
    """
    nft_owned_query = """
    UPDATE nft_owned SET user_id = %s where token_id = %s;
    """
    txn_id = str(datetime.timestamp(datetime.now()))        
    transaction_query = """INSERT INTO Transactions_contains 
    (txn_id, amount, status, token_id) VALUES 
    (%s, %s,%s,%s)"""
    buy_query = """INSERT INTO Buy_Txn
    (txn_id, user_id) VALUES 
    (%s, %s)"""
    sell_query = """INSERT INTO Sell_Txn
    (txn_id, user_id) VALUES 
    (%s, %s)"""
    audit_id = str(datetime.timestamp(datetime.now()))
    audit_query = """
    INSERT INTO Audit (audit_id,audit_description, audit_path, audit_timestamp)
    VALUES (%s,'NFT Transferred',%s,now())
    """
    nft_log_query = """
    INSERT INTO NFT_Log (audit_id, token_id)
    VALUES (%s,%s)
    """
    audit_path = "Audit/_NFT_log"
    try:
        db_info = get_config()
        conn = psycopg2.connect(**db_info)
        cursor = conn.cursor()
        cursor.execute(nft_query, (amount,nft))
        cursor.execute(nft_owned_query, (buyer,nft))
        cursor.execute(transaction_query, (txn_id,amount,True,nft))
        cursor.execute(buy_query,(txn_id,buyer))
        cursor.execute(sell_query,(txn_id,seller))
        cursor.execute(audit_query,(audit_id,audit_path))
        cursor.execute(nft_log_query,(audit_id,nft))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as ex:
        print(ex)
        st.write("Something went wrong during the transaction")
    finally:
        cursor.close()
        conn.close()

#0 List Tables
query = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)' ORDER BY relname;"
table_name = ""
try:
    all_table_names = query_db(query)["relname"].tolist()
    table_name = st.selectbox("Choose a table to view data", all_table_names)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if table_name:
    sql_table = f"SELECT * FROM {table_name};"
    try:
        df = query_db(sql_table)
        st.dataframe(df)
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )

#1 List Users, currency held and their balances
query = """ 
select  a.name AS User,c.currency_name AS Currency, balance AS Balance from currency_holds c
join Wallet_has w on w.wallet_id = c.wallet_id
join Account a on a.user_id = w.user_id
order by a.name, c.currency_name;
"""
st.write("List Users, currency held and their balances")
st.dataframe(query_db(query))


#2 List NFTs either created or owned by specific user
selection = "Created"
selection = st.radio(
    "List NFTs either created or owned by specific user",
    ('Created', 'Owned'))
query = f"""SELECT a.name as user, a.user_id FROM Account a
join {"nft_owned" if selection == "Owned" else "nft_created"} n on n.user_id = a.user_id
ORDER BY user;"""
user = ""
query = query_db(query)
users = query["user"].tolist()
users_ids = query["user_id"].tolist()
user = st.selectbox("Choose a user to view owned NFTs", range(len(users)), format_func=lambda x: users[x])
query = f"""SELECT n.token_name AS Token, n.nft_url AS URL, n.current_value AS Value FROM NFT n 
JOIN {"nft_owned" if selection == "Owned" else "nft_created"} nft_o ON nft_o.token_id = n.token_id 
WHERE nft_o.user_id ='{users_ids[user]}'
ORDER BY Token;"""
df = query_db(query)
df["value"] = pd.to_numeric(df["value"])        
st.dataframe(df)


#3 List Users with Credit Card Expiry between the given years
expiry_year = st.slider('Select range to list users with credit card expiry', 2022, 2030, (2024,2026))
query = f"""
SELECT a.name, f.bank_name , f.expiry_year as year  FROM  Account a
JOIN Financial_Information_contains f
ON a.user_id=f.user_id
WHERE f.expiry_year between {expiry_year[0]} AND {expiry_year[1]}
ORDER BY a.name, f.bank_name;
"""
df = query_db(query)
st.dataframe(df)


#4 List NFT transactions including Buyer, Seller and the amount of transaction
st.write("List NFT transactions including Buyer, Seller and the amount of transaction")
query = """
SELECT n.token_name AS Token, a1.name as Buyer, a2.name as Seller, t.amount as amount FROM NFT n
JOIN Transactions_contains t on n.token_id = t.token_id
JOIN Buy_Txn b on t.txn_id = b.txn_id
JOIN Sell_Txn s on t.txn_id = s.txn_id
JOIN Account a1 on b.user_id = a1.user_id
JOIN Account a2 on s.user_id = a2.user_id
ORDER BY Token, Amount
"""
df = query_db(query)
df["amount"] = pd.to_numeric(df["amount"])
st.dataframe(df)


#5 List count of NFTs created and owned by Users
st.write("List count of NFTs created and owned by Users")
query = """
WITH NFOC as (
SELECT a.name, n.token_id FROM  Account a
JOIN Nft_Owned n
ON a.user_id=n.user_id
UNION
SELECT a.name, n.token_id FROM  Account a
JOIN Nft_Created n
ON a.user_id=n.user_id
)
SELECT name AS User, count( nfoc.token_id) as Count FROM NFOC
GROUP BY name
ORDER BY name
"""
df = query_db(query)
st.dataframe(df)

#7 Display log history of a NFT Token
nft_query = f"""
SELECT n.token_name, n.token_id FROM NFT n
ORDER BY token_name;
"""    
nft_query = query_db(nft_query)
nfts = nft_query["token_name"].tolist()
nft_ids = nft_query["token_id"].tolist()

nft = st.selectbox(f"Select NFT for it's log history ",  range(len(nfts)), format_func=lambda x: nfts[x])

nft_query = f"""
SELECT a.audit_description AS "Description", a.audit_timestamp AS "Timestamp" FROM Audit a
JOIN NFT_Log nl ON a.audit_id = nl.audit_id
WHERE nl.token_id = '{nft_ids[nft]}'
ORDER BY a.audit_timestamp;
"""
df = query_db(nft_query)
st.dataframe(df)


#6 Buy and Sell NFTs amongst users
query1 = """
SELECT a.name as user, a.user_id  FROM Account a
ORDER BY user;
"""
query2 = """SELECT a.name as user, a.user_id FROM Account a
join nft_owned n on n.user_id = a.user_id
ORDER BY user;"""

user1, user2, nft = "" , "", ""
users1_ids, user2_ids = [],[]
users1, users2 = None, None
query1 = query_db(query1)
users1 = query1["user"].tolist()
users1_ids = query1["user_id"].tolist()

query2 = query_db(query2)
users2 = query2["user"].tolist()
users2_ids = query2["user_id"].tolist()

user1 = st.selectbox("Select Buyer",  range(len(users1)), format_func=lambda x: users1[x])
user2 = st.selectbox("Select Seller",  range(len(users2)), format_func=lambda x: users2[x], index=0)

nft_query = f"""
select n.token_name, n.token_id from nft n
join nft_owned no on n.token_id = no.token_id
join Account a on a.user_id = no.user_id
where a.user_id = '{users2_ids[user2]}'
ORDER BY token_name;
"""    
nft_query = query_db(nft_query)
nfts = nft_query["token_name"].tolist()
nft_ids = nft_query["token_id"].tolist()

nft = st.selectbox(f"Select NFT owned by {users2[user2]} ",  range(len(nfts)), format_func=lambda x: nfts[x])

curval_query = f"""
select n.current_value from nft n
where n.token_id = '{nft_ids[nft]}'
"""
st.write(f"Current Value of {nfts[nft]} = {query_db(curval_query).current_value[0]} tokens")
amount = st.number_input('Amount')

if st.button('Transact'):
    if float(amount) != 0.0:
        if users1_ids[user1] != users2_ids[user2]:
            transact(users1_ids[user1], users2_ids[user2], nft_ids[nft], amount)
            st.write("Transaction Successful")
        else:
            st.write("Buyer and Seller cannot be the same")    
    else:
        st.write("Please provide an amount")

