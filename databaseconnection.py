import oracledb
from authenticationdata import user, password, dsn


def connectionoracle():
    oracledb.init_oracle_client(config_dir="/home/juliano/Wallet")
    return oracledb.connect(user=user, password=password, dsn=dsn)
    



