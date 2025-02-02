#!/usr/bin/env python

from eth_tester.exceptions import TransactionFailed
from pytest import raises, mark
from utils import longTo32Bytes, fix, AssertLog, TokenDelta, BuyWithCash, nullAddress
from constants import BID, ASK, YES, NO


def test_create_ask_with_shares_fill_with_shares(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    completeSetFees = fix('12', '0.02') * market.getNumTicks()

    # 1. both accounts buy a complete set
    with BuyWithCash(cash, fix('12', market.getNumTicks()), contractsFixture.accounts[1], "buy complete set"):
        assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = contractsFixture.accounts[1])
    with BuyWithCash(cash, fix('12', market.getNumTicks()), contractsFixture.accounts[2], "buy complete set"):
        assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = contractsFixture.accounts[2])
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)

    # 2. create ASK order for YES with YES shares for escrow
    assert yesShareToken.approve(createOrder.address, fix(12), sender = contractsFixture.accounts[1])
    askOrderID = createOrder.publicCreateOrder(ASK, fix(12), 60, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender = contractsFixture.accounts[1])
    assert askOrderID
    assert cash.balanceOf(contractsFixture.accounts[1]) == 0
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)

    # 3. fill ASK order for YES with NO shares
    assert noShareToken.approve(fillOrder.address, fix(12), sender = contractsFixture.accounts[2])
    amountRemaining = fillOrder.publicFillOrder(askOrderID, fix(12), longTo32Bytes(42), False, "0x0000000000000000000000000000000000000000", sender = contractsFixture.accounts[2])
    creatorFee = completeSetFees * 3 / 5
    fillerFee = completeSetFees * 2 / 5
    assert amountRemaining == 0
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('12', '60') - creatorFee
    assert cash.balanceOf(contractsFixture.accounts[2]) == fix('12', '40') - fillerFee
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == 0

def test_create_ask_with_shares_fill_with_cash(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy a complete set with account 1
    with BuyWithCash(cash, fix('12', market.getNumTicks()), contractsFixture.accounts[1], "buy complete set"):
        assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = contractsFixture.accounts[1])
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12), "Account 1 should have 12 shares of outcome 1"
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12), "Account 1 should have 12 shares of outcome 2"

    # 2. create ASK order for YES with YES shares for escrow
    assert yesShareToken.approve(createOrder.address, fix(12), sender = contractsFixture.accounts[1])
    askOrderID = createOrder.publicCreateOrder(ASK, fix(12), 60, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender = contractsFixture.accounts[1])
    assert askOrderID, "Order ID should be non-zero"
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)

    # 3. fill ASK order for YES with cash
    with BuyWithCash(cash, fix('12', '60'), contractsFixture.accounts[2], "filling order"):
        amountRemaining = fillOrder.publicFillOrder(askOrderID, fix(12), longTo32Bytes(42), False, "0x0000000000000000000000000000000000000000", sender = contractsFixture.accounts[2])
    assert amountRemaining == 0
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('12', '60')
    assert cash.balanceOf(contractsFixture.accounts[2]) == 0
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == 0

def test_create_ask_with_cash_fill_with_shares(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 2
    with BuyWithCash(cash, fix('12', market.getNumTicks()), contractsFixture.accounts[2], "buy complete set"):
        assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender=contractsFixture.accounts[2])
    assert cash.balanceOf(contractsFixture.accounts[2]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)

    # 2. create ASK order for YES with cash escrowed
    with BuyWithCash(cash, fix('12', '40'), contractsFixture.accounts[1], "buy complete set"):
        askOrderID = createOrder.publicCreateOrder(ASK, fix(12), 60, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender=contractsFixture.accounts[1])
    assert askOrderID
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0

    # 3. fill ASK order for YES with shares of NO
    assert noShareToken.approve(fillOrder.address, fix(12), sender = contractsFixture.accounts[2])
    amountRemaining = fillOrder.publicFillOrder(askOrderID, fix(12), longTo32Bytes(42), False, "0x0000000000000000000000000000000000000000", sender = contractsFixture.accounts[2])
    assert amountRemaining == 0, "Amount remaining should be 0"
    assert cash.balanceOf(contractsFixture.accounts[1]) == 0
    assert cash.balanceOf(contractsFixture.accounts[2]) == fix('12', '40')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == 0

def test_create_ask_with_cash_fill_with_cash(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. create ASK order for YES with cash escrowed
    with BuyWithCash(cash, fix('12', '40'), contractsFixture.accounts[1], "create order"):
        askOrderID = createOrder.publicCreateOrder(ASK, fix(12), 60, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender= contractsFixture.accounts[1])
    assert askOrderID
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0

    # 2. fill ASK order for YES with cash
    with BuyWithCash(cash, fix('12', '60'), contractsFixture.accounts[2], "create order"):
        amountRemaining = fillOrder.publicFillOrder(askOrderID, fix(12), longTo32Bytes(42), False, "0x0000000000000000000000000000000000000000", sender = contractsFixture.accounts[2])
    assert amountRemaining == 0
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert cash.balanceOf(contractsFixture.accounts[2]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == 0

def test_create_bid_with_shares_fill_with_shares(contractsFixture, cash, market, universe):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    totalProceeds = fix('12', market.getNumTicks())
    marketCreatorFee = totalProceeds / market.getMarketCreatorSettlementFeeDivisor()
    reporterFee = totalProceeds / universe.getOrCacheReportingFeeDivisor()
    completeSetFees = marketCreatorFee + reporterFee

    # 1. buy complete sets with both accounts
    with BuyWithCash(cash, fix('12', market.getNumTicks()), contractsFixture.accounts[1], "buy complete set"):
        assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = contractsFixture.accounts[1])
    with BuyWithCash(cash, fix('12', market.getNumTicks()), contractsFixture.accounts[2], "buy complete set"):
        assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = contractsFixture.accounts[2])
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert cash.balanceOf(contractsFixture.accounts[2]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)

    # 2. create BID order for YES with NO shares escrowed
    assert noShareToken.approve(createOrder.address, fix(12), sender = contractsFixture.accounts[1])
    orderID = createOrder.publicCreateOrder(BID, fix(12), 60, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender = contractsFixture.accounts[1])
    assert orderID
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0

    # 3. fill BID order for YES with shares of YES
    assert yesShareToken.approve(fillOrder.address, fix(12), sender = contractsFixture.accounts[2])

    orderFilledEventLog = {
	    "eventType": 3,
	    "addressData": [nullAddress, contractsFixture.accounts[1] , contractsFixture.accounts[2]],
	    "uint256Data": [60, 0, YES, 0, 0, completeSetFees, fix(12),  contractsFixture.contracts['Time'].getTimestamp(), 0, 0],
    }
    with AssertLog(contractsFixture, 'OrderEvent', orderFilledEventLog):
        leftoverInOrder = fillOrder.publicFillOrder(orderID, fix(12), longTo32Bytes(42), False, "0x0000000000000000000000000000000000000000", sender = contractsFixture.accounts[2])
        assert leftoverInOrder == 0

    creatorFee = completeSetFees * 2 / 5
    fillerFee = completeSetFees * 3 / 5
    creatorPayment = fix('12', '40') - creatorFee
    fillerPayment = fix('12', '60') - fillerFee
    assert cash.balanceOf(contractsFixture.accounts[1]) == creatorPayment
    assert cash.balanceOf(contractsFixture.accounts[2]) == fillerPayment
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)

def test_create_bid_with_shares_fill_with_cash(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 1
    with BuyWithCash(cash, fix('12', market.getNumTicks()), contractsFixture.accounts[1], "buy complete set"):
        assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = contractsFixture.accounts[1])
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)

    # 2. create BID order for YES with NO shares escrowed
    assert noShareToken.approve(createOrder.address, fix(12), sender = contractsFixture.accounts[1])
    orderID = createOrder.publicCreateOrder(BID, fix(12), 60, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender = contractsFixture.accounts[1])
    assert orderID
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0

    # 3. fill BID order for YES with cash
    with BuyWithCash(cash, fix('12', '40'), contractsFixture.accounts[2], "fill order"):
        leftoverInOrder = fillOrder.publicFillOrder(orderID, fix(12), longTo32Bytes(42), False, "0x0000000000000000000000000000000000000000", sender = contractsFixture.accounts[2])
    assert leftoverInOrder == 0
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('12', '40')
    assert cash.balanceOf(contractsFixture.accounts[2]) == 0
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)

def test_create_bid_with_cash_fill_with_shares(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 2
    with BuyWithCash(cash, fix('12', market.getNumTicks()), contractsFixture.accounts[2], "buy complete set"):
        assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = contractsFixture.accounts[2])
    assert cash.balanceOf(contractsFixture.accounts[2]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)

    # 2. create BID order for YES with cash escrowed
    with BuyWithCash(cash, fix('12', '60'), contractsFixture.accounts[1], "create order"):
        orderID = createOrder.publicCreateOrder(BID, fix(12), 60, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender = contractsFixture.accounts[1])
    assert orderID
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0

    # 3. fill BID order for YES with shares of YES
    assert yesShareToken.approve(fillOrder.address, fix(12), sender = contractsFixture.accounts[2])
    leftoverInOrder = fillOrder.publicFillOrder(orderID, fix(12), longTo32Bytes(42), False, "0x0000000000000000000000000000000000000000", sender = contractsFixture.accounts[2])
    assert leftoverInOrder == 0
    assert cash.balanceOf(contractsFixture.accounts[1]) == 0
    assert cash.balanceOf(contractsFixture.accounts[2]) == fix('12', '60')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)

def test_create_bid_with_cash_fill_with_cash(contractsFixture, cash, market):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. create BID order for YES with cash escrowed
    with BuyWithCash(cash, fix('12', '60'), contractsFixture.accounts[1], "create order"):
        orderID = createOrder.publicCreateOrder(BID, fix(12), 60, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender = contractsFixture.accounts[1])
    assert orderID
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0

    # 2. fill BID order for YES with cash
    with BuyWithCash(cash, fix('12', '40'), contractsFixture.accounts[2], "create order"):
        leftoverInOrder = fillOrder.publicFillOrder(orderID, fix(12), longTo32Bytes(42), False, "0x0000000000000000000000000000000000000000", sender = contractsFixture.accounts[2])
    assert leftoverInOrder == 0
    assert cash.balanceOf(contractsFixture.accounts[1]) == fix('0')
    assert cash.balanceOf(contractsFixture.accounts[2]) == fix('0')
    assert yesShareToken.balanceOf(contractsFixture.accounts[1]) == fix(12)
    assert yesShareToken.balanceOf(contractsFixture.accounts[2]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[1]) == 0
    assert noShareToken.balanceOf(contractsFixture.accounts[2]) == fix(12)

import contextlib
@contextlib.contextmanager
def placeholder_context():
    yield None

@mark.parametrize('type,outcome,displayPrice,orderSize,creatorYesShares,creatorNoShares,creatorCost,fillSize,fillerYesShares,fillerNoShares,fillerCost,expectMakeRaise,expectedMakerYesShares,expectedMakerNoShares,expectedMakerPayout,expectTakeRaise,expectedFillerYesShares,expectedFillerNoShares,expectedFillerPayout', [
    # | ------ ORDER ------ |   | ------ CREATOR START ------ |   | ------ FILLER START ------ |  | ------- CREATOR FINISH -------  |    | ------- FILLER FINISH -------  |
    #   type,outcome,  price,   size,    yes,     no,   cost,   size,    yes,     no,   cost,  raise,    yes,     no,      pay,    raise,    yes,     no,      pay,
    (    BID,    YES,  '0.6',  '12',    '0',    '0',  '7.2',  '12',   '12',    '0',    '0',  False,   '12',    '0',       '0',    False,    '0',    '0',     '7.2'),
    (    BID,    YES,  '0.6',  '12',    '0',   '12',    '0',  '12',   '12',    '0',    '0',  False,    '0',    '0',   '4.704',    False,    '0',    '0',   '7.056'),
    (    BID,    YES,  '0.6',  '12',    '0',    '0',  '7.2',  '12',    '0',    '0',  '4.8',  False,   '12',    '0',       '0',    False,    '0',   '12',       '0'),
    (    BID,    YES,  '0.6',  '12',    '0',   '12',    '0',  '12',    '0',    '0',  '4.8',  False,    '0',    '0',     '4.8',    False,    '0',   '12',       '0'),

    (    BID,    YES,  '0.6',  '24',    '0',   '12',  '7.2',  '24',   '24',    '0',    '0',  False,   '12',    '0',   '4.704',    False,    '0',    '0',  '14.256'),
    (    BID,    YES,  '0.6',  '24',    '0',   '12',  '7.2',  '24',    '0',    '0',  '9.6',  False,   '12',    '0',     '4.8',    False,    '0',   '24',       '0'),
    (    BID,    YES,  '0.6',  '24',    '0',    '0', '14.4',  '24',   '12',    '0',  '4.8',  False,   '24',    '0',       '0',    False,    '0',   '12',     '7.2'),
    (    BID,    YES,  '0.6',  '24',    '0',   '24',    '0',  '24',   '12',    '0',  '4.8',  False,    '0',    '0',   '9.504',    False,    '0',   '12',   '7.056'),

    (    BID,    YES,  '0.6',  '24',    '0',   '12',  '7.2',  '24',   '12',    '0',  '4.8',  False,   '12',    '0',   '4.704',    False,    '0',   '12',   '7.056'),

    (    BID,     NO,  '0.6',  '12',    '0',    '0',  '7.2',  '12',    '0',   '12',    '0',  False,    '0',   '12',       '0',    False,    '0',    '0',     '7.2'),
    (    BID,     NO,  '0.6',  '12',   '12',    '0',    '0',  '12',    '0',   '12',    '0',  False,    '0',    '0',   '4.704',    False,    '0',    '0',   '7.056'),
    (    BID,     NO,  '0.6',  '12',    '0',    '0',  '7.2',  '12',    '0',    '0',  '4.8',  False,    '0',   '12',       '0',    False,   '12',    '0',       '0'),
    (    BID,     NO,  '0.6',  '12',   '12',    '0',    '0',  '12',    '0',    '0',  '4.8',  False,    '0',    '0',     '4.8',    False,   '12',    '0',       '0'),

    (    BID,     NO,  '0.6',  '24',   '12',    '0',  '7.2',  '24',    '0',   '24',    '0',  False,    '0',   '12',   '4.704',    False,    '0',    '0',  '14.256'),
    (    BID,     NO,  '0.6',  '24',   '12',    '0',  '7.2',  '24',    '0',    '0',  '9.6',  False,    '0',   '12',     '4.8',    False,   '24',    '0',       '0'),
    (    BID,     NO,  '0.6',  '24',    '0',    '0', '14.4',  '24',    '0',   '12',  '4.8',  False,    '0',   '24',       '0',    False,   '12',    '0',     '7.2'),
    (    BID,     NO,  '0.6',  '24',   '24',    '0',    '0',  '24',    '0',   '12',  '4.8',  False,    '0',    '0',   '9.504',    False,   '12',    '0',   '7.056'),

    (    BID,     NO,  '0.6',  '24',   '12',    '0',  '7.2',  '24',    '0',   '12',  '4.8',  False,    '0',   '12',   '4.704',    False,   '12',    '0',   '7.056'),

    (    ASK,    YES,  '0.6',  '12',   '12',    '0',    '0',  '12',    '0',    '0',  '7.2',  False,    '0',    '0',     '7.2',    False,   '12',    '0',       '0'),
    (    ASK,    YES,  '0.6',  '12',    '0',    '0',  '4.8',  '12',    '0',    '0',  '7.2',  False,    '0',   '12',       '0',    False,   '12',    '0',       '0'),
    (    ASK,    YES,  '0.6',  '12',   '12',    '0',    '0',  '12',    '0',   '12',    '0',  False,    '0',    '0',   '7.056',    False,    '0',    '0',   '4.704'),
    (    ASK,    YES,  '0.6',  '12',    '0',    '0',  '4.8',  '12',    '0',   '12',    '0',  False,    '0',   '12',       '0',    False,    '0',    '0',     '4.8'),
])
def test_parametrized(type, outcome, displayPrice, orderSize, creatorYesShares, creatorNoShares, creatorCost, fillSize, fillerYesShares, fillerNoShares, fillerCost, expectMakeRaise, expectedMakerYesShares, expectedMakerNoShares, expectedMakerPayout, expectTakeRaise, expectedFillerYesShares, expectedFillerNoShares, expectedFillerPayout, contractsFixture, cash, market):
    fixture = contractsFixture
    # TODO: add support for wider range markets
    displayPrice = int(float(displayPrice) * market.getNumTicks())
    assert displayPrice < market.getNumTicks()
    assert displayPrice > 0

    orderSize = fix(orderSize)
    creatorYesShares = fix(creatorYesShares)
    creatorNoShares = fix(creatorNoShares)
    creatorCost = fix(creatorCost, market.getNumTicks())

    fillSize = fix(fillSize)
    fillerYesShares = fix(fillerYesShares)
    fillerNoShares = fix(fillerNoShares)
    fillerCost = fix(fillerCost, market.getNumTicks())

    expectedMakerYesShares = fix(expectedMakerYesShares)
    expectedMakerNoShares = fix(expectedMakerNoShares)
    expectedMakerPayout = fix(expectedMakerPayout, market.getNumTicks())

    expectedFillerYesShares = fix(expectedFillerYesShares)
    expectedFillerNoShares = fix(expectedFillerNoShares)
    expectedFillerPayout = fix(expectedFillerPayout, market.getNumTicks())

    creatorAddress = contractsFixture.accounts[1]
    creatorKey = contractsFixture.accounts[1]
    fillerAddress = contractsFixture.accounts[2]
    fillerKey = contractsFixture.accounts[2]

    completeSets = fixture.contracts['CompleteSets']
    createOrder = fixture.contracts['CreateOrder']
    fillOrder = fixture.contracts['FillOrder']
    yesShareToken = fixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('ShareToken', market.getShareToken(NO))

    def acquireShares(outcome, amount, approvalAddress, sender):
        if amount == 0: return
        with BuyWithCash(cash, amount * market.getNumTicks(), sender, "The sender didn't get cost deducted for complete set sale"):
            assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender)
        if outcome == YES:
            assert yesShareToken.approve(approvalAddress, amount, sender = sender)
            assert noShareToken.transfer(contractsFixture.accounts[8], amount, sender = sender)
        if outcome == NO:
            assert yesShareToken.transfer(contractsFixture.accounts[8], amount, sender = sender)
            assert noShareToken.approve(approvalAddress, amount, sender = sender)

    # create order
    acquireShares(YES, creatorYesShares, createOrder.address, sender = creatorKey)
    acquireShares(NO, creatorNoShares, createOrder.address, sender = creatorKey)
    with BuyWithCash(cash, creatorCost, creatorKey, "create order"):
        with raises(TransactionFailed) if expectMakeRaise else placeholder_context():
            orderID = createOrder.publicCreateOrder(type, orderSize, displayPrice, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), longTo32Bytes(42), False, nullAddress, sender = creatorKey)
    # fill order
    acquireShares(YES, fillerYesShares, fillOrder.address, sender = fillerKey)
    acquireShares(NO, fillerNoShares, fillOrder.address, sender = fillerKey)
    with raises(TransactionFailed) if expectTakeRaise else placeholder_context():
        # Cannot use BuyWithCash here, the test might deposit 0 CASH, but acquire large amounts CASH via selling existing shares
        cash.faucet(fillerCost, sender=fillerKey)
        fillOrder.publicFillOrder(orderID, fillSize, longTo32Bytes(42), False, "0x0000000000000000000000000000000000000000", sender=fillerKey)

    # assert final state
    assert cash.balanceOf(creatorAddress) == expectedMakerPayout
    assert cash.balanceOf(fillerAddress) == expectedFillerPayout
    assert yesShareToken.balanceOf(creatorAddress) == expectedMakerYesShares
    assert yesShareToken.balanceOf(fillerAddress) == expectedFillerYesShares
    assert noShareToken.balanceOf(creatorAddress) == expectedMakerNoShares
    assert noShareToken.balanceOf(fillerAddress) == expectedFillerNoShares
