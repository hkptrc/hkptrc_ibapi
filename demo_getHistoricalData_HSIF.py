import hkptrc_ibapi
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

    raw_data = app.get_historical_data(
        tickerid=8900,                                      # Positive integer as unique identifier
        ibcontract=ibcontract,
        endDateTime='20230626 16:15:00 HongKong',           # Format: yyyymmdd hh:mm:ss xxx
        durationStr='30 D',
        barSizeSetting='1 day',
        RTH=0,                                              # 0: RTH and ATH data, 1: only RTH data
    )

    print(raw_data)

    app.disconnect()



