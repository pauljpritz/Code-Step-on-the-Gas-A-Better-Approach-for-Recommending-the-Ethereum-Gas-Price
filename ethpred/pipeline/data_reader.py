import json
from pprint import pprint


def read_data(cnf: dict):
    with open(cnf['data']['eth_price_file']) as f:
        eth_price = json.load(f)
    pprint(eth_price)


    gas_price = []
    with open(cnf['data']['gas_price_file'], 'r') as f:
        if cnf['testing']:
            count = 0
            for line in f:
                gas_price.append(json.loads(line))
                count += 1
                if count >= 100:
                    break
        else:
            for line in f:
                gas_price.append(json.loads(line))
    pprint(gas_price[0])

    return eth_price, gas_price