import string
from typing import List, Dict

# The datamodel classes are provided by the IMC Prosperity simulator backend.
from datamodel import OrderDepth, UserId, TradingState, Order

class Trader:
    """
    Trader algorithm for IMC Prosperity Round 1 ( EMERALDS and TOMATOES )
    Version 2: Refined Strategies based on log analysis
    
    ---
    Version 2 Historical Insights:
    - Run PnL: ~1900
    - EMERALDS: Employs passive market making using limit orders slightly inside the massive
      system spread (Bid: 9996 / Ask: 10004). This consistently captures the spread.
    - TOMATOES: Abandons tight midpoint pegging. Instead, quotes directly inside the 
      existing best_ask and best_bid (capturing an enormous ~12 tick spread) jumping to the top of LOB. 
      This yields a tremendous profit buffer against adverse selection.
    """
    
    POSITION_LIMIT = 20

    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Dictionary containing the list of orders to be placed for each product
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # Position tracking to ensure we don't breach limits
            current_position = state.position.get(product, 0)
            
            ###########################################
            # STRATEGY FOR EMERALDS
            ###########################################
            if product == 'EMERALDS':
                # Fair value is perfectly 10,000.
                acceptable_price = 10000
                
                # Robustly get best ask and bid without relying on dict order
                best_ask = min(order_depth.sell_orders.keys()) if len(order_depth.sell_orders) > 0 else None
                best_bid = max(order_depth.buy_orders.keys()) if len(order_depth.buy_orders) > 0 else None

                # 1. Aggressively take liquidity if the price is extremely favorable crossing the spread
                if best_ask is not None and best_ask < acceptable_price:
                    best_ask_amount = order_depth.sell_orders[best_ask]
                    buy_amount = min(self.POSITION_LIMIT - current_position, -best_ask_amount)
                    if buy_amount > 0:
                        print("EMERALDS AGGRESSIVE BUY", str(buy_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, buy_amount))
                        current_position += buy_amount
                
                if best_bid is not None and best_bid > acceptable_price:
                    best_bid_amount = order_depth.buy_orders[best_bid]
                    sell_amount = min(self.POSITION_LIMIT + current_position, best_bid_amount)
                    if sell_amount > 0:
                        print("EMERALDS AGGRESSIVE SELL", str(sell_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -sell_amount))
                        current_position -= sell_amount

                # 2. Passive market making
                # The system primarily bids around 9992 and asks around 10008.
                # We quote superior limits to capture the spread when takers buy/sell.
                bid_price = 9996
                ask_price = 10004
                
                if current_position < self.POSITION_LIMIT:
                    buy_vol = self.POSITION_LIMIT - current_position
                    if buy_vol > 0:
                        orders.append(Order(product, bid_price, buy_vol))
                        
                if current_position > -self.POSITION_LIMIT:
                    sell_vol = self.POSITION_LIMIT + current_position
                    if sell_vol > 0:
                        orders.append(Order(product, ask_price, -sell_vol))

            ###########################################
            # STRATEGY FOR TOMATOES
            ###########################################
            elif product == 'TOMATOES':
                # Tomatoes have a floating price.
                best_ask = min(order_depth.sell_orders.keys()) if len(order_depth.sell_orders) > 0 else None
                best_bid = max(order_depth.buy_orders.keys()) if len(order_depth.buy_orders) > 0 else None
                
                if best_ask is not None and best_bid is not None:
                    # Old strategy quoted tightly at mid +/- 1, suffering massive adverse selection
                    # because the true spread is usually large (average ~13).
                    # Now we will quote slightly inside the current best bid/ask to jump to the top
                    # of the LOB while capturing a vast spread buffer against directional moves.
                    buy_price = best_bid + 1
                    sell_price = best_ask - 1
                    
                    # Safety check: Ensure we maintain a solid minimum spread of 2 ticks
                    # to protect against adverse selection if the outer spread miraculously collapsed.
                    if sell_price - buy_price < 2:
                        mid = (best_ask + best_bid) / 2
                        buy_price = int(mid) - 1
                        sell_price = int(mid) + 1
                    
                    # Dynamically adjust quantities based on position to avoid inventory risk
                    buy_vol = min(self.POSITION_LIMIT - current_position, self.POSITION_LIMIT)
                    sell_vol = min(self.POSITION_LIMIT + current_position, self.POSITION_LIMIT)
                    
                    if current_position < self.POSITION_LIMIT and buy_vol > 0:
                        orders.append(Order(product, buy_price, buy_vol))
                            
                    if current_position > -self.POSITION_LIMIT and sell_vol > 0:
                        orders.append(Order(product, sell_price, -sell_vol))

            result[product] = orders
            
        # Optional return payloads: target conversion integer and dictionary for next state passing
        traderData = "SAMPLE_STATE_PERSISTENCE"
        conversions = 0
        
        return result, conversions, traderData
