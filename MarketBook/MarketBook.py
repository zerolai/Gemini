import datetime
import os

class MarketBook(object):
    def __init__(self, symbol, tickSize):
        self.__Book={ 'bid':{}, 'ask':{} }
        self.__BestBidPrice=0.0
        self.__BestAskPrice=float("inf")

        self.__Symbol=symbol
        self.__TickSize=tickSize
        self.__Trades=[]

    def __str__(self):
        return "symbol="+self.__Symbol+", ticksize="+self.__TickSize+ \
            ", Bid="+str(self.__BestBidPrice)+", BidQty="+str(self.__Book['bid'][self.__BestBidPrice])+ \
            ", Ask="+str(self.__BestAskPrice)+", AskQty="+str(self.__Book['ask'][self.__BestAskPrice])

    def printBook(self, depth, nonZero):
        book = self.getBook(depth, nonZero);
        os.system('cls')
        print (' '*29, 'Bid || Ask')
        for bookDepth in book:
            print('{0:<15f} @ {1:>15f} || {2:<15f} @ {3:>15f}'.format(bookDepth[0][1], bookDepth[0][0], bookDepth[1][0], bookDepth[1][1]))
        spread=int((self.__BestAskPrice - self.__BestBidPrice) / self.__TickSize) * self.__TickSize
        print ('Ask=' + str(self.__BestAskPrice))
        print ('Bid=' + str(self.__BestBidPrice))
        print ('Spread=' + str(spread))

        noOfTrades = len(self.__Trades)
        lastTrade = self.__Trades[noOfTrades-1] if noOfTrades>0 else (0, 0, 0)
        print ('Last=' + str(lastTrade[2]) + ' @ ' + str(lastTrade[1]) + ' at ' + str(lastTrade[0]))

    #setter    
    def processChange(self, change):
        if change['reason']=='initial':
            self.initBook(change)
        else: #place/cancel/trade
            self.updateBook(change)

    def processTrade(self, trade):
        self.__Trades.append((datetime.datetime.utcnow().time(), trade["price"], trade["amount"]))

    def initBook(self, initial):
        self.updateBook(initial)

    def updateBook(self, update):
        px=float(update['price'])
        qty=float(update['remaining'])
        self.__Book[update['side']][px]=qty

        if update['side']=='bid':
            if px<self.__BestBidPrice:
                return
            else: #>=self.__BestBidPrice
                if qty>0:
                    self.__BestBidPrice=px
                elif px==self.__BestBidPrice:
                    self.__BestBidPrice, tmp=self.getBid(0)
        else: #ask
            if px>self.__BestAskPrice:
                return
            else: #<=self.__BestAskPrice
                if qty>0:
                    self.__BestAskPrice=px
                elif px==self.__BestAskPrice:
                    self.__BestAskPrice, tmp=self.getAsk(0)

        assert self.__BestBidPrice>=0 and self.__BestAskPrice>=0, 'negative bid or ask' + ', Bid=' + str(self.__BestBidPrice) + ', Ask=' + str(self.__BestAskPrice)


    #getters

    def getBid(self, offset=0):
        for i in sorted(self.__Book['bid'].keys(), reverse=True):
            if self.__Book["bid"][i] > 0:
                bidPrice = i + (offset * self.__TickSize)
                bidQty = self.__Book["bid"][bidPrice] if bidPrice in self.__Book['bid'].keys() else 0
                return bidPrice, bidQty
                break
        return 0, 0


    def getNonZeroBid(self, offset=0):
        for i in sorted(self.__Book['bid'].keys(), reverse=True):
            if self.__Book["bid"][i] > 0:
                if offset==0:
                    return i, self.__Book["bid"][i]
                offset-=1
        return 0, 0
 
    def getAsk(self, offset=0):
        for i in sorted(self.__Book['ask'].keys(), reverse=False):
            if self.__Book["ask"][i] > 0:
                askPrice = i - (offset * self.__TickSize)
                askQty = self.__Book["ask"][askPrice] if askPrice in self.__Book['ask'].keys() else 0
                return askPrice, askQty
        return 0, 0

    def getNonZeroAsk(self, offset=0):
        for i in sorted(self.__Book['ask'].keys(), reverse=False):
            if self.__Book["ask"][i] > 0:
                if offset==0:
                    return i, self.__Book["ask"][i]
                offset-=1
        return 0, 0

    def getBook(self, depth, nonZero):
        if nonZero==True:
            return [ (self.getNonZeroBid(i), self.getNonZeroAsk(i)) for i in list(range(depth))]
        return [ (self.getBid(i), self.getAsk(i)) for i in list(range(depth))]



class GeminiBook(MarketBook):
    TICKSIZEMAP = { 'btcusd':0.01,
                    'ethusd':0.01,
                    'ethbtc':0.00001,
                    'zecusd':0.01,
                    'zecbtc':0.00001,
                    'zeceth':0.0001}

    def __init__(self, symbol):
        tickSize = self.TICKSIZEMAP[symbol] if symbol in self.TICKSIZEMAP.keys() else 0
        assert tickSize>0, 'tick size not found'
        MarketBook.__init__(self, symbol, tickSize)