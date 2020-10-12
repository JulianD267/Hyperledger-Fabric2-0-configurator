#!/bin/bash

echo "Gimme logs!"
rm -rf inv_block_commit.csv inv_tx_invalid_logs.csv inv_tx_times.csv inv_block_commit_logs.txt inv_tx_invalid_logs.txt inv_tx_times.txt
docker logs peer0.org1.dredev.de 2>&1 | grep "kvledger" | tr -d [] > inv_block_commit_logs.txt
docker logs peer0.org1.dredev.de 2>&1 | grep "invalid" | tr -d [] > inv_tx_invalid_logs.txt
docker logs peer0.org1.dredev.de 2>&1 | grep "finished chaincode:" | tr -d [] > inv_tx_times.txt


while IFS= read -r line
do
   block_no=$(echo $line | awk '/block/{ print $12 }')
   tx_cnt=$(echo $line | awk '/block/{ print $14 }')
   ms_block=$(echo $line | awk '/block/{ print $17 }' | tr -d ms)
   #echo "Block $block_no with $tx_cnt tx in $ms_block"
   printf '%s;%s;%s\n' $block_no $tx_cnt $ms_block >> inv_block_commit.csv
done < "inv_block_commit_logs.txt"

FAILED=1
while IFS= read -r line
do
  block_no=$(echo $line | awk '/ValidateAndPrepareBatch/{ print $10 }')
  tx_cnt=$(echo $line | awk '/ValidateAndPrepareBatch/{ print $13 }')
  tx_id=$(echo $line | awk '/ValidateAndPrepareBatch/{ print $15 }')
  printf '%s;%s;%s\n' $block_no $tx_cnt $tx_id >> inv_tx_invalid_logs.csv
done < "inv_tx_invalid_logs.txt"

while IFS= read -r line
do
   ts_ms=$(echo $line | awk '/channel/{ print $13 }' | tr -d ms)
   tx_cnt=$(echo $line | awk '/channel/{ print $15 }' | tr -d txID=)
   #echo "Block $block_no with $tx_cnt tx in $ms_block"
   printf '%s;%s\n' $tx_cnt $ts_ms >> inv_tx_times.csv
done < "inv_tx_times.txt"
