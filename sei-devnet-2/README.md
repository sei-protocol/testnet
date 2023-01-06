# sei-devnet-2


## Join as a validator in sei-devnet-2

1. Please submit a gentx to the `./gentx` folder through a pull request or by copy pasting the gentx output and asking one of the Sei team members to make a pull request.

```
export MONIKER=sei-node-0
export CHAIN_ID=sei-devnet-2
export ACCOUNT_NAME=admin
export STARTING_BALANCE=10000sei
export STARTING_DELEGATION=10000sei

seid init $MONIKER --chain-id $CHAIN_ID
# Create account
seid keys add $ACCOUNT_NAME
# Set account address based on above
export ACCOUNT_ADDRESS=
# Create a genesis account with starting balance
seid add-genesis-account $ACCOUNT_ADDRESS $STARTING_BALANCE
# Create gentx with validator starting delegation amount
seid gentx $ACCOUNT_NAME $STARTING_DELEGATION --chain-id $CHAIN_ID
```
