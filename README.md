# Lottery Contract

The following are the features achieved by the contract:
1. Users can enter lottery with eth based on a USD fees
2. Admin will choose when the lottery is over
3. The lottery will select a random winner

## Code walkthrough

1. You can find the contracts in the contracts folder. The main contract file is Lottery.sol
2. In the contracts/test folder, we have the mocks required for random number generator and the dollar value of ethereum. Here we are using chainlink oracles to do these two tasks for us.
4. You can find tests in the tests folder. 
3. You can find the deploy scripts in scripts folder. Use the deploy.py to run the script

```
brownie run scripts/deploy.py --network rinkeby
```

Todo: Create more tests