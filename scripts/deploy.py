from brownie import Lottery, network, config, MockV3Aggregator
from scripts.helpful_scripts import (
    get_account,
    deploy_mocks,
    LOCAL_BLOCKCHAIN_ENV,
    get_contract,
    fund_with_link,
)
import time


def deploy_lottery():
    account = get_account()
    # if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
    #     price_feed_address = config["networks"][network.show_active()][
    #         "eth_usd_price_feed"
    #     ]
    # else:
    #     deploy_mocks()
    #     price_feed_address = MockV3Aggregator[-1].address

    # print(f"price feed address: {price_feed_address}")
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
    )
    print(f"Contract Deployed to {lottery}")
    print(f"lottery price {lottery.getPrice()}")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("Lottery has started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    entrance_fees = lottery.getEntranceFees()
    tx = lottery.enter({"from": account, "value": entrance_fees + 1000000})
    tx.wait(1)
    print("You entered the lottery")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund the contract with link
    # then end the lottery
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
