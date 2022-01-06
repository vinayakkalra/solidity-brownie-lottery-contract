from brownie import Lottery, config, network
from scripts.helpful_scripts import get_account


def enter_lottery():
    lottery = Lottery[-1]
    account = get_account()
    entrance_fees = lottery.getEntranceFees()
    print(entrance_fees)
    lottery.enter({"from": account, "value": entrance_fees + 100})


# def withdraw():
#     fund_me = FundMe[-1]
#     account = get_account()
#     fund_me.withdraw({"from":account})


def main():
    enter_lottery()
