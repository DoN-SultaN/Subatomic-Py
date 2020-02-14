import platform
import os
import re
import slickrpc


class CustomProxy(slickrpc.Proxy):
    def __init__(self,
                 service_url=None,
                 service_port=None,
                 conf_file=None,
                 timeout=3000):
        config = dict()
        if conf_file:
            config = slickrpc.ConfigObj(conf_file)
        if service_url:
            config.update(self.url_to_conf(service_url))
        if service_port:
            config.update(rpcport=service_port)
        elif not config.get('rpcport'):
            config['rpcport'] = 7771
        self.conn = self.prepare_connection(config, timeout=timeout)


def def_credentials(chain):
    rpcport = ''
    ac_dir = ''
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Win64' or operating_system == 'Windows':
        ac_dir = '%s/komodo/' % os.environ['APPDATA']
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
    with open(coin_config_file, 'r') as f:
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
            elif re.search('rpcport', l):
                rpcport = l.replace('rpcport=', '')
    if len(rpcport) == 0:
        if chain == 'KMD':
            rpcport = 7771
        else:
            print("rpcport not in conf file, exiting")
            print("check "+coin_config_file)
            exit(1)

    return CustomProxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)))


def get_orderbook_data(rpc_proxy, base, rel):
    orderbook_data = rpc_proxy.DEX_orderbook("", "0", base, rel)
    return orderbook_data


def refresh_bids_list(rpc_proxy, base, rel, bids_list):
    orderbook_data = get_orderbook_data(rpc_proxy, base, rel)
    bids_data = orderbook_data["bids"]
    print(orderbook_data)
    for bid in bids_data:
        bids_list.delete(*bids_list.get_children())
        bids_list.insert("", "end", text=bid["id"], values=[bid["price"], bid["baseamount"], bid["relamount"], bid["timestamp"], bid["hash"]])


def refresh_asks_list(rpc_proxy, base, rel, asks_list):
    orderbook_data = get_orderbook_data(rpc_proxy, base, rel)
    asks_data = orderbook_data["asks"]
    print(orderbook_data)
    for ask in asks_data:
        asks_list.delete(*asks_list.get_children())
        asks_list.insert("", "end", text=ask["id"], values=[ask["price"], ask["baseamount"], ask["relamount"], ask["timestamp"], ask["hash"]])


def refresh_orders_list(rpc_proxy, base, rel, bids_list, asks_list):
    refresh_bids_list(rpc_proxy, base, rel, bids_list)
    refresh_asks_list(rpc_proxy, base, rel, asks_list)