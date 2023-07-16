import hkptrc_ibapi
import time
from ibapi.contract import Contract as ibContract
from ibapi.order import Order as ibOrder

if __name__ == '__main__':
    app = hkptrc_ibapi.hkptrc_ibApp('127.0.0.1', 7496, 1)
    app.get_order_id()                                      # Prepare the next valid order id

    # Contract Details
    ibcontract = ibContract()
    ibcontract.symbol = 'AAPL'
    ibcontract.secType = 'STK'
    ibcontract.currency = 'USD'
    ibcontract.exchange = 'SMART'

    # Order Details
    iborder = ibOrder()
    iborder.action = 'BUY'                                  # 'BUY' or 'SELL'
    iborder.orderType = 'MKT'
    iborder.totalQuantity = 1
    iborder.orderId = app.nextorderId                       # Use the next valid order id
    app.nextorderId += 1                                    # Increment id by 1 for the next use

    app.placeOrder(iborder.orderId, ibcontract, iborder)    # Place the order

    time.sleep(5)                                           # Give some time for the operation

    app.disconnect()



