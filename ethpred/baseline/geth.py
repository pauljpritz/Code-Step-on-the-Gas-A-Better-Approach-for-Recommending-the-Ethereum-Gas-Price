from typing import Dict

import numpy as np


MAX_PRICE: int = 500_000_000_000


class GethPredictor:
    """Geth 'algorithm' to suggest a price is very straight forward
    It simply uses a tunable percentile for the minimum price in the past blocks
    The percentile and number of look-behind blocks can be set when starting geth

    Original logic can be found here:
    https://github.com/ethereum/go-ethereum/blob/master/eth/gasprice/gasprice.go

    Args:
        min_prices: A mapping of block height to minimum price
    """
    def __init__(self, min_prices: Dict[int, int]):
        self.prices = min_prices

    def suggest_price(self,
                      block_number: int,
                      blocks_count: int = 20,
                      percentile: float = 60):
        """Mimics the logic of geth to suggest a gas price

        Args:
            block_number: Block number for which the price should be predicted.
                          Block must be in the min_prices give during initialization
            blocks_count: This number will be multiplied by 5 to obtain
                          the number of blocks to look behind and divided by 2
                          to find the number of empty blocks to skip
            percentile: This is the percentile to use when suggesting the price
        """
        if percentile <= 0:
            percentile = 0
        if percentile >= 100:
            percentile = 100
        max_blocks = blocks_count * 5
        max_empty = blocks_count // 2

        prices = []
        current_block_number = block_number - 1
        while block_number >= 0 and len(prices) < max_blocks:
            price = self.prices[current_block_number]
            if price == 0 and max_empty >= 0:
                max_empty -= 1
                continue
            prices.append(price)
            current_block_number -= 1
        suggested_price = int(np.percentile(prices, q=percentile))
        if suggested_price >= MAX_PRICE:
            suggested_price = MAX_PRICE
        return suggested_price