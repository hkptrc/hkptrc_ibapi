from ibapi.wrapper import EWrapper as Wrapper_HKPTRC
from ibapi.client import EClient as Client_HKPTRC
from threading import Thread
import queue
import time

ended = object()

class HKPTRC_Wrapper(Wrapper_HKPTRC):
    def __init__(self):
        self.hkptrccontractdedict = {}
        self.hkptrchistoricaldict = {}

    def historicalData(self, tickerid, bar):
        self.hkptrchistoricaldict.setdefault(tickerid, queue.Queue()) if tickerid not in self.hkptrchistoricaldict.keys() else None
        bardata = (bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume)
        self.hkptrchistoricaldict[tickerid].put(bardata)

    def historicalDataEnd(self, tickerid, start: str, end: str):
        self.hkptrchistoricaldict.setdefault(tickerid, queue.Queue()) if tickerid not in self.hkptrchistoricaldict.keys() else None
        self.hkptrchistoricaldict[tickerid].put(ended)

    def contractDetails(self, tickerid, contractdetails):
        self.hkptrccontractdedict[tickerid] = queue.Queue()
        self.hkptrccontractdedict[tickerid].put(contractdetails)


class HKPTRC_Client(Client_HKPTRC):
    def __init__(self, wrapper):
        Client_HKPTRC.__init__(self, wrapper)

    def resolve(self, ibcontract):
        self.reqContractDetails(0, ibcontract)
        try:
            contractDetails = self.hkptrccontractdedict[0].get(timeout=5)
            ibcontract = contractDetails.contract
        except: pass
        return ibcontract

    def get_historical_data(self, tickerid, ibcontract, barSizeSetting, durationStr, RTH, endDateTime='', whatToShow='TRADES', formatDate=1, keepUpToDate=False):
        self.hkptrchistoricaldict[tickerid] = queue.Queue()
        contents = contentqueue(self.hkptrchistoricaldict[tickerid])
        if ibcontract.secType == 'FUT': ibcontract = self.resolve(ibcontract)
        self.reqHistoricalData(tickerid, ibcontract, endDateTime, durationStr, barSizeSetting, whatToShow, RTH, formatDate, keepUpToDate, [])
        return contents.get()

    def get_market_data(self, ibcontract, tickerid):
        if ibcontract.secType == 'FUT': ibcontract = self.resolve(ibcontract)
        self.reqMktData(tickerid, ibcontract, '', False, False, [])

    def get_positions(self):
        self.position_data = queue.Queue()
        self.reqPositions()

    def get_order_id(self):
        self.reqIds(-1)
        time.sleep(2)

class contentqueue(object):
    def __init__(self, _queue):
        self._queue = _queue

    def get(self, timeout=5):
        contents = []
        finished = False
        while not finished:
            try:
                element = self._queue.get(timeout=timeout)
                finished = True if element is ended else contents.append(element)
            except queue.Empty: finished = True
        return contents

class hkptrc_ibApp(HKPTRC_Wrapper, HKPTRC_Client):
    def __init__(self, ipaddress, portid, clientid):
        HKPTRC_Wrapper.__init__(self)
        HKPTRC_Client.__init__(self, wrapper=self)
        self.tick_data = queue.Queue()
        self.connect(ipaddress, portid, clientid)
        self.nextorderId = None
        thread = Thread(target=self.run)
        thread.start()
        time.sleep(2)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId

    def tickPrice(self, tickerid, tickType, price, attrib):
        tick_dict = {tickerid: {}}
        if tickType == 1: tick_dict[tickerid]['bid_price'] = price
        elif tickType == 2: tick_dict[tickerid]['ask_price'] = price
        elif tickType == 4: tick_dict[tickerid]['last_price'] = price
        elif tickType == 6: tick_dict[tickerid]['day_high'] = price
        elif tickType == 7: tick_dict[tickerid]['day_low'] = price
        if tickType in [1, 2, 4, 6, 7]: self.tick_data.put(tick_dict)

    def tickSize(self, tickerid, tickType, size):
        tick_dict = {tickerid: {}}
        if tickType == 0: tick_dict[tickerid]['bid_size'] = size
        elif tickType == 3: tick_dict[tickerid]['ask_size'] = size
        elif tickType == 5: tick_dict[tickerid]['last_size'] = size
        if tickType in [0, 3, 5]: self.tick_data.put(tick_dict)

    def tickGeneric(self, tickerid, tickType, value):
        tick_dict = {tickerid: {}}
        if tickType == 24: tick_dict[tickerid]['implied_vol'] = value
        if tickType in [24]: self.tick_data.put(tick_dict)

    def position(self, account, contract, pos, avgCost):
        self.position_data.put({'code':contract.symbol, 'pos':int(pos), 'avg cost':avgCost})
