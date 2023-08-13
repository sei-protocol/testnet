# sei-devnet-2


## Join as a validator in sei-devnet-2

1. Please submit a gentx to the `./gentx` folder through a pull request or by copy pasting the gentx output and asking one of the Sei team members to make a pull request.

**Make sure you're on the `sei-devnet-2` branch!**

```bash
export MONIKER=<your-moniker>
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

[example PR](https://github.com/sei-protocol/testnet/pull/1820)

Persistent Peer Info:

```bash
1977382a8b085b60d6545f78910979e34514120a@162.19.232.153:51956,1fb59ca4fe3d3a701768443fbfdfb5bb9070fade@3.73.138.242:26656,5db854fbd78e5fe067186cb3ffc0a1c11b450ac7@35.156.223.252:26656,78c0ec4851128584ce9b2fca3a4c11c33209980f@213.239.217.52:40656,86c92bd3d34f43bdf03f20c6a1b863e9cf355df1@65.109.58.243:26656,27238e2f804bf28a14c186a2e0f0ceaae0d2588f@sei-devnet.p2p.brocha.in:30519,2b77ddc9781da52e25d7d8dc293c89e1144ac9e7@88.99.219.120:51656,324e5e1cc936620118e7d2f124801298f128a688@136.244.82.24:26656,2b77ddc9781da52e25d7d8dc293c89e1144ac9e7@88.99.219.120:51656,6383e60e7e482f38d172f1189dd58f480bffb555@65.108.192.123:41656,aae1c52e0aad2bdc62a3b1c64147c9f5cb2b4fe2@136.243.88.91:3030,5950b4f74ceca6db1b1f26ada8a3ef42f9144c9a@65.109.70.23:11956
```
