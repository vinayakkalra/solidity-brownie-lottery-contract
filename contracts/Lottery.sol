// SPDX-License-Identifier: MIT

pragma solidity >=0.6.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface public ethUsdPriceFeed;
    address owner;

    uint256 public randomness;
    address payable public recentWinner;
    uint256 public fee;
    bytes32 public keyhash;

    // enum creates states in a smart contract. here open is 0 stage, closed is 1 nd calculating winner is 2
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LOTTERY_STATE public lottery_state;

    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _priceFeed,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeed);
        usdEntryFee = 50 * 10**18;
        owner = msg.sender;
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }

    function getPrice() public view returns (uint256) {
        (, int256 answer, , , ) = ethUsdPriceFeed.latestRoundData();
        return uint256(answer * 10000000000);
    }

    function getConversionRate(uint256 eth) public view returns (uint256) {
        uint256 ethPrice = getPrice();
        return (eth * ethPrice) / 1000000000000000000;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not an Owner");
        _;
    }

    function enter() public payable {
        // require lottery state to be open
        require(lottery_state == LOTTERY_STATE.OPEN, "Lottery should be open");
        //  $50 minimum
        require(
            getConversionRate(msg.value) >= usdEntryFee,
            "Need to spend more ETH"
        );
        players.push(payable(msg.sender));
    }

    function getEntranceFees() public view returns (uint256) {
        //
        // uint256 minimumUsd = 50 * 10**18;
        uint256 price = getPrice();
        uint256 precesion = 1 * 10**18;
        return (usdEntryFee * precesion) / price;
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "cant start a new lottery yet"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You are't there yet"
        );
        require(_randomness > 0, "Random not found");

        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        // reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }

    // additional testing functions
    function getLotteryAddresses()
        public
        view
        returns (address payable[] memory)
    {
        return players;
    }
}
