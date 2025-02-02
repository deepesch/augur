#!/usr/bin/env python

from eth_tester.exceptions import TransactionFailed
from pytest import raises, mark
from utils import longTo32Bytes, longToHexString, fix, AssertLog, BuyWithCash, nullAddress
from constants import BID, ASK, YES, NO

def test_cancelBid(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']
    orders = contractsFixture.contracts['Orders']

    orderType = BID
    amount = fix(1)
    fxpPrice = 60
    outcomeID = YES
    tradeGroupID = longTo32Bytes(42)
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    creatorInitialShares = yesShareToken.balanceOf(contractsFixture.accounts[1])
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()
    with BuyWithCash(cash, fix(fxpPrice), contractsFixture.accounts[1], "The sender didn't get cost deducted for create order"):
        orderID = createOrder.publicCreateOrder(orderType, amount, fxpPrice, market.address, outcomeID, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, False, nullAddress, sender=contractsFixture.accounts[1])

    assert orderID, "Order ID should be non-zero"
    assert orders.getOrderCreator(orderID), "Order should have an owner"

    orderEventLog = {
        "universe": universe.address,
        "market": market.address,
	    "eventType": 1,
	    "addressData": [nullAddress, contractsFixture.accounts[1], nullAddress],
	    "uint256Data": [0, 0, 0, fix('1', '60'), 0, 0, 0,  contractsFixture.contracts['Time'].getTimestamp(), 0, 0],
    }
    with AssertLog(contractsFixture, 'OrderEvent', orderEventLog):
        assert(cancelOrder.cancelOrder(orderID, sender=contractsFixture.accounts[1]) == 1), "cancelOrder should succeed"

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert(cash.balanceOf(contractsFixture.accounts[1]) == fix('60')), "Maker's cash balance should be order size"
    assert(marketInitialCash == cash.balanceOf(market.address)), "Market's cash balance should be the same as before the order was placed"
    assert(creatorInitialShares == yesShareToken.balanceOf(contractsFixture.accounts[1])), "Maker's shares should be unchanged"
    assert(marketInitialYesShares == yesShareToken.totalSupply()), "Market's yes shares should be unchanged"
    assert marketInitialNoShares == noShareToken.totalSupply(), "Market's no shares should be unchanged"

def test_cancelAsk(contractsFixture, cash, market):
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']
    orders = contractsFixture.contracts['Orders']

    orderType = ASK
    amount = fix(1)
    fxpPrice = 60
    outcomeID = 1
    tradeGroupID = longTo32Bytes(42)
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    creatorInitialShares = yesShareToken.balanceOf(contractsFixture.accounts[1])
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()
    with BuyWithCash(cash, fix(100 - fxpPrice), contractsFixture.accounts[1], "create order"):
        orderID = createOrder.publicCreateOrder(orderType, amount, fxpPrice, market.address, outcomeID, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, False, nullAddress, sender=contractsFixture.accounts[1])
    assert(orderID != bytearray(32)), "Order ID should be non-zero"
    assert orders.getOrderCreator(orderID), "Order should have an owner"

    assert(cancelOrder.cancelOrder(orderID, sender=contractsFixture.accounts[1]) == 1), "cancelOrder should succeed"

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert(marketInitialCash == cash.balanceOf(market.address)), "Market's cash balance should be the same as before the order was placed"
    assert(creatorInitialShares == yesShareToken.balanceOf(contractsFixture.accounts[1])), "Maker's shares should be unchanged"
    assert(marketInitialYesShares == yesShareToken.totalSupply()), "Market's yes shares should be unchanged"
    assert marketInitialNoShares == noShareToken.totalSupply(), "Market's no shares should be unchanged"

def test_cancelWithSharesInEscrow(contractsFixture, cash, market, universe):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']
    orders = contractsFixture.contracts['Orders']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    totalProceeds = fix('12', market.getNumTicks())
    marketCreatorFee = totalProceeds / market.getMarketCreatorSettlementFeeDivisor()
    reporterFee = totalProceeds / universe.getOrCacheReportingFeeDivisor()
    completeSetFees = marketCreatorFee + reporterFee

    # buy complete sets
    with BuyWithCash(cash, fix('12', market.getNumTicks()), contractsFixture.accounts[1], "buy complete set"):
        assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = contractsFixture.accounts[1])
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)

    creatorInitialShares = yesShareToken.balanceOf(contractsFixture.accounts[1])
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()

    # create BID order for YES with NO shares escrowed
    assert noShareToken.approve(createOrder.address, fix(12), sender = contractsFixture.accounts[1])
    orderID = createOrder.publicCreateOrder(BID, fix(12), 60, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender = contractsFixture.accounts[1])
    assert orderID
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0

    # now cancel the order
    assert(cancelOrder.cancelOrder(orderID, sender=contractsFixture.accounts[1]) == 1), "cancelOrder should succeed"

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert(marketInitialCash == cash.balanceOf(market.address)), "Market's cash balance should be the same as before the order was placed"
    assert(creatorInitialShares == yesShareToken.balanceOf(contractsFixture.accounts[1])), "Maker's shares should be unchanged"
    assert(marketInitialYesShares == yesShareToken.totalSupply()), "Market's yes shares should be unchanged"
    assert marketInitialNoShares == noShareToken.totalSupply(), "Market's no shares should be unchanged"

def test_cancelWithSharesInEscrowAsk(contractsFixture, cash, market, universe):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']
    orders = contractsFixture.contracts['Orders']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    totalProceeds = fix('12', market.getNumTicks())
    marketCreatorFee = totalProceeds / market.getMarketCreatorSettlementFeeDivisor()
    reporterFee = totalProceeds / universe.getOrCacheReportingFeeDivisor()
    completeSetFees = marketCreatorFee + reporterFee

    # buy complete sets
    with BuyWithCash(cash, fix('12', market.getNumTicks()), contractsFixture.accounts[1], "buy complete set"):
        assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = contractsFixture.accounts[1])
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)

    creatorInitialShares = yesShareToken.balanceOf(contractsFixture.accounts[1])
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()

    # create ASK order for YES with YES shares escrowed
    assert noShareToken.approve(createOrder.address, fix(12), sender = contractsFixture.accounts[1])
    orderID = createOrder.publicCreateOrder(ASK, fix(12), 60, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender = contractsFixture.accounts[1])
    assert orderID
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)

    # now cancel the order
    assert(cancelOrder.cancelOrder(orderID, sender=contractsFixture.accounts[1]) == 1), "cancelOrder should succeed"

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert(marketInitialCash == cash.balanceOf(market.address)), "Market's cash balance should be the same as before the order was placed"
    assert(creatorInitialShares == yesShareToken.balanceOf(contractsFixture.accounts[1])), "Maker's shares should be unchanged"
    assert(marketInitialYesShares == yesShareToken.totalSupply()), "Market's yes shares should be unchanged"
    assert marketInitialNoShares == noShareToken.totalSupply(), "Market's no shares should be unchanged"

def test_exceptions(contractsFixture, cash, market):
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']

    orderType = BID
    amount = fix(1)
    fxpPrice = 60
    outcomeID = YES
    tradeGroupID = longTo32Bytes(42)
    with BuyWithCash(cash, fix(fxpPrice), contractsFixture.accounts[1], "create order"):
        orderID = createOrder.publicCreateOrder(orderType, amount, fxpPrice, market.address, outcomeID, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, False, nullAddress, sender=contractsFixture.accounts[1])
    assert(orderID != bytearray(32)), "Order ID should be non-zero"

    # cancelOrder exceptions
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(longTo32Bytes(0), sender=contractsFixture.accounts[1])
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(longTo32Bytes(1), sender=contractsFixture.accounts[1])
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(orderID, sender=contractsFixture.accounts[2])
    assert(cancelOrder.cancelOrder(orderID, sender=contractsFixture.accounts[1]) == 1), "cancelOrder should succeed"
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(orderID, sender=contractsFixture.accounts[1])

def test_cancelOrders(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']
    orders = contractsFixture.contracts['Orders']

    orderType = BID
    amount = fix(1)
    fxpPrice = 60
    outcomeID = YES
    tradeGroupID = longTo32Bytes(42)
    orderIDs = []
    for i in range(10):
        with BuyWithCash(cash, fix(fxpPrice + i), contractsFixture.accounts[0], "create order"):
            orderIDs.append(createOrder.publicCreateOrder(orderType, amount, fxpPrice + i, market.address, outcomeID, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, False, nullAddress))

    for i in range(10):
        assert orders.getAmount(orderIDs[i]) == amount

    assert cancelOrder.cancelOrders(orderIDs)

    for i in range(10):
        assert orders.getAmount(orderIDs[i]) == 0
