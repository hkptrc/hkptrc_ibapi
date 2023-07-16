import hkptrc_ibapi
import queue
from ibapi.contract import Contract as ibContract

if __name__ == '__main__':
    app = hkptrc_ibapi.hkptrc_ibApp('127.0.0.1', 7496, 1)

    # Contract Details
    ibcontract = ibContract()
    ibcontract.symbol = 'HSI'
    ibcontract.secType = 'FUT'
    ibcontract.currency = 'HKD'
    ibcontract.exchange = 'HKFE'
    ibcontract.lastTradeDateOrContractMonth = '202307'

    app.get_market_data(ibcontract, 9900)                   # (ibContract(), Positive integer as unique identifier)

    keep_loop = True
    while keep_loop:
        try:
            tick_data = app.tick_data.get(timeout=1)
            print(tick_data)
        except queue.Empty:
            keep_loop = False

    app.disconnect()



