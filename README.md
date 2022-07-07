# Jobs for UTO8 Contracts

## Unbox

###### This job will look for BlindBox which has not been unboxed in SalesProvider contract and check the unbox time, if the unbox time is due the job will call generateRandomNumber function to get a random number from Chainlink

### How to run

```bash
docker build -t unbox -f dockerfiles/Unbox.Dockerfile .
docker run --env-file Unbox-VAR.env unbox
```

### Enviroment variables

```env
Web3_HTTP_Provider=xxxxxxxxxxxxx
SalesProvider_Contract_Address=xxxxxxxxxxxxx
Piamon_Contract_Address=xxxxxxxxxxxxx
Contract_Owner_Address=xxxxxxxxxxxxx
BlindBox_Id=0
Contract_Owner_Key=xxxxxxxxxxxxx
RABBITMQ_HOST=xxxxxxxxxxxxx
```
