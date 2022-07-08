import os
import json

# get all files within the gentx folder
gentx_files = os.listdir('gentx')

invalids = ""

with open('gentx-output.csv', 'w') as outfile:
    outfile.write("") # clean file

for file in gentx_files:
    print(f'Extracting info from {file}')
    f = open('gentx/' + file, 'r')
    data = json.load(f)

    validatorData = data['body']['messages'][0]
    moniker = validatorData['description']['moniker']
    rate = float(validatorData['commission']['rate']) * 100
    delegator_addr = validatorData['delegator_address']
    validator_addr = validatorData['validator_address']
    exp = validatorData['value']
### Basic validation ###
    if exp['denom'] != 'usei':
        invalids += f'[!] Invalid denomination for validator: {moniker} {exp["denom"]} \n'

    if int(exp['amount'] ) /10000000 != 1.0:
        invalids += f'[!] Invalid amount for validator: {moniker} {int(exp["amount"] ) /10000000}\n'

    with open('gentx-output.csv', 'a') as outfile:
        outfile.write(f"{delegator_addr} {validator_addr} {moniker}\n")

with open('gentx-output.csv', 'a') as outfile:
    outfile.write(invalids)

print('Written to file gentx-output.csv')
