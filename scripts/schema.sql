-- Authors: Ajinkya Vijay Sonawane, Sidharth Purohit
DROP TABLE IF EXISTS Account;
CREATE TABLE Account (
    user_id varchar(128) primary key,
    name varchar(256),
    age integer,
    bio varchar(512)
);

DROP TABLE IF EXISTS Audit;
CREATE TABLE Audit (
    audit_id varchar(30) primary key,
    audit_description varchar(128) not null,
    audit_path varchar(128) not null,
    audit_timestamp timestamp not null
);

DROP TABLE IF EXISTS Login_requires;
CREATE TABLE Login_requires (
    login_id varchar(128) primary key,
    password varchar(128) not null,
    security_question varchar(256) not null,
    security_answer varchar(256) not null,
    logged_in boolean default false,
    user_id varchar(128) not null,
    foreign key (user_id) references Account (user_id)
);

DROP TABLE IF EXISTS NFT;
CREATE TABLE NFT(
    token_id varchar(128) primary key,
    token_name varchar(128) not null,
    nft_url varchar(256) not null,
    current_value decimal not null
);

DROP TABLE IF EXISTS NFT_created;
CREATE TABLE NFT_created(
    token_id varchar(128),
    user_id varchar(128),
    primary key(token_id,user_id),
    foreign key (user_id) references Account (user_id),
    foreign key (token_id) references NFT (token_id)
);

DROP TABLE IF EXISTS NFT_owned;
CREATE TABLE NFT_owned(
    token_id varchar(128),
    user_id varchar(128),
    primary key(token_id,user_id),
    foreign key (user_id) references Account (user_id),
    foreign key (token_id) references NFT (token_id)
);

DROP TABLE IF EXISTS Financial_Information_contains;
CREATE TABLE Financial_Information_contains(
    fin_id varchar(30) primary key,
    card_number varchar(20) not null,
    card_cvv integer not null,
    bank_name varchar(256) not null,
    expiry_month integer not null,
    expiry_year integer not null,
    user_id varchar(128) not null,
    foreign key (user_id) references Account (user_id)
);

DROP TABLE IF EXISTS Transactions_contains;
CREATE TABLE Transactions_contains (
    txn_id varchar(128) primary key,
    amount decimal not null,
    status boolean default false,
    token_id varchar(128) not null,
    txn_timestamp timestamp, 
    foreign key (token_id) references NFT (token_id)
);

DROP TABLE IF EXISTS Buy_TXN;
CREATE TABLE Buy_TXN(
    txn_id varchar(128) primary key,
    user_id varchar(128) not null,
    foreign key (user_id) references Account (user_id),
    foreign key (txn_id) references Transactions_contains (txn_id)
);

DROP TABLE IF EXISTS Sell_TXN;
CREATE TABLE Sell_TXN(
    txn_id varchar(128) primary key,
    user_id varchar(128) not null,
    foreign key (user_id) references Account (user_id),
    foreign key (txn_id) references Transactions_contains (txn_id)
);

DROP TABLE IF EXISTS Wallet_has;
CREATE TABLE WALLET_has(
    wallet_id varchar(128) primary key,
    wallet_address varchar(256) not null,
    user_id varchar(128) unique not null,
    foreign key (user_id) references Account (user_id)
);

DROP TABLE IF EXISTS Currency_holds;
CREATE TABLE Currency_holds(
    currency_id serial primary key,
    currency_name varchar(128) not null,
    balance decimal not null, 
    wallet_id varchar(30) not null,
    foreign key (wallet_id) references Wallet_has (wallet_id)
);

DROP TABLE IF EXISTS Login_Log;
CREATE TABLE Login_Log(
    audit_id varchar(30),
    login_id varchar(128),
    primary key (audit_id,login_id),
    foreign key (login_id) references Login_requires (login_id) on delete cascade,
    foreign key (audit_id) references Audit (audit_id) on delete cascade
);

DROP TABLE IF EXISTS Account_Log;
CREATE TABLE Account_Log(
    audit_id varchar(30),
    user_id varchar(128),
    primary key (audit_id,user_id),
    foreign key (user_id) references Account (user_id) on delete cascade,
    foreign key (audit_id) references Audit (audit_id) on delete cascade
);

DROP TABLE IF EXISTS NFT_Log;
CREATE TABLE NFT_Log(
    audit_id varchar(30),
    token_id varchar(128),
    primary key (audit_id,token_id),
    foreign key (token_id) references NFT (token_id) on delete cascade,
    foreign key (audit_id) references Audit (audit_id) on delete cascade
);