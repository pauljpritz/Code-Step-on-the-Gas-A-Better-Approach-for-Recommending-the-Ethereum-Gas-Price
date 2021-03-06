from datetime import datetime

import pandas as pd
import numpy as np

from .calc_distributions import generate_distribution
from . import normalizers


def convert_to_dataframe(eth_prices: dict, gas_price: list, cnf: dict):
    features = cnf['data']['features']
    nested_features = cnf['data']['nested_features']

    gas_price_dict = parse_gas_price_data(cnf, features, gas_price, nested_features)

    data = join_datasets(cnf, eth_prices, gas_price_dict)


    print("before resampling: \n", data.head())

    data = resample_data(data, cnf)

    data, data_normalizers = normalise_data(data, cnf)

    print(data[data.isna().any(axis=1)])

    print(data.head())

    return data, data_normalizers


def resample_data(data: pd.DataFrame, cnf: dict):
    if cnf['data']['resample']:
        data = data.resample(cnf['data']['resample']).mean()
        data = data.fillna(method='pad')
    return data


def parse_gas_price_data(cnf, features, gas_price, nested_features):
    gas_price_dict = {}
    for obs in range(len(gas_price)):
        gas_price_dict[obs] = {}
        for feature in features:
            if feature in gas_price[obs]:
                gas_price_dict[obs][feature] = gas_price[obs][feature]
            else:
                gas_price_dict[obs][feature] = None
        if 'timestamp' in gas_price[obs]:
            gas_price_dict[obs]['time'] = datetime.fromtimestamp(gas_price[obs]['timestamp'])

        for feature in nested_features:
            key = list(feature.keys())[0]
            val = feature[key]
            if key in gas_price[obs] and val in gas_price[obs][key]:
                gas_price_dict[obs][key] = gas_price[obs][key][val]
            else:
                gas_price_dict[obs][key] = None

        if cnf['type'] == 'distribution' and 'transactions' in gas_price[obs]:
            gas_price_dict[obs]['mean'], gas_price_dict[obs]['std_dev'] = generate_distribution(
                gas_price[obs]['transactions'])

            if cnf['data']['inc_transactions']:
                for i in range(len(gas_price[obs]['transactions'])):
                    gas_price_dict[obs]['gas_price_' + str(i)] = gas_price[obs]['transactions'][i][
                        'gas_price']
    return gas_price_dict


def join_datasets(cnf, eth_prices, gas_price_dict):
    if isinstance(eth_prices, dict):
        eth_price_df = pd.DataFrame.from_dict(eth_prices)
    elif isinstance(eth_prices, pd.DataFrame):
        eth_price_df = eth_prices
    else:
        raise NotImplementedError
    eth_price_df['date'] = pd.to_datetime(eth_price_df['date'])
    eth_price_df = eth_price_df[cnf['data']['eth_price_features']]
    gas_price_df = pd.DataFrame.from_dict(gas_price_dict, orient='index')

    gas_price_df = gas_price_df.dropna(axis='rows', subset=['time']).fillna(0).sort_values(
        by='time')
    eth_price_df = eth_price_df.dropna(axis='rows', subset=['date']).fillna(0).sort_values(
        by='date')

    data = pd.merge_asof(gas_price_df, eth_price_df, left_on='time', right_on='date',
                         direction='backward')
    data.set_index('time', inplace=True, drop=False)

    # Add the lagged columns if any
    lag_cols = cnf['data']['lagged_cols']
    lagged_data = pd.DataFrame(data[lag_cols], index=data.index)
    lagged_data = lagged_data.shift(1, freq='D')
    lagged_data.columns = [i + '_lagged' for i in lag_cols]

    data = pd.merge_asof(data, lagged_data, left_index=True, right_index=True, direction='nearest')
    data = data[
        (data['time'] > cnf['data']['start_date']) & (data['time'] <= cnf['data']['end_date'])]

    data = data.drop(columns=['time', 'date'])

    return data



def scale_array(array, scale_method):
    normalizer = normalizers.create(scale_method)
    scaled = normalizer.fit_transform(array)
    return scaled, normalizer


def remove_outliers(data: pd.DataFrame, columns):
    for column in columns:
        if column not in data:
            continue
        series = data[column]
        mean = series.mean()
        stdev = series.std()
        data = data[(series - mean).abs() <= 1.5 * stdev]
    return data


def normalise_data(data: pd.DataFrame, cnf):
    data = remove_outliers(data, cnf['data'].get('remove_outliers', []))
    scaling = cnf['data']['scaling']
    normalizers = {}
    for column in scaling['columns']:
        if column in data:
            scaled, normalizer = scale_array(data[column], scaling['normalizer'])
            data[column] = scaled
            normalizers[column] = normalizer
    # print('after scaling\n', data.head())
    return data, normalizers
