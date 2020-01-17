import json
import gzip as gz
from datetime import datetime
from pprint import pprint


def read_data(cnf: dict):
    start_time = datetime.fromisoformat(cnf['data']['start_date'])
    end_time = datetime.fromisoformat(cnf['data']['end_date'])

    with open(cnf['data']['eth_price_file']) as f:
        eth_price = json.load(f)

    gas_price = []
    with gz.open(cnf['data']['gas_price_file'], 'r') as f:
        if cnf['testing']:
            count = 0
            for line in f:
                gas_price.append(json.loads(line))
                count += 1
                if count >= 1000:
                    break
        else:
            for line in f:
                current = json.loads(line)
                if 'timestamp' in current:
                    gas_price.append(current)
                    time = datetime.fromtimestamp(current['timestamp'])
                    if time <= start_time or time > end_time:
                        break

    return eth_price, gas_price
