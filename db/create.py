from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Boolean

metadata = MetaData()

user  = Table('users', metadata,
    Column('id', Integer(), primary_key=True),
    Column('user_id', Integer(), nullable=False),
    Column('chat_id', Integer(), nullable=False),
    Column('is_admin', Boolean(), nullable=False),
    Column('user_name', String(), nullable=False),
)

wallets = Table('wallets', metadata,
    Column('id', Integer(), primary_key=True),
    Column('user', ForeignKey("users.user_id"), nullable=False),
    Column('chain', String(), nullable=False),
    Column('wallet', String(), nullable=False),
    Column('w_name', String(), nullable=False),
)