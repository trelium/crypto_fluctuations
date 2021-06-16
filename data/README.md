# Cryptocurrency Telegram Price Fluctuation Notifier and Predictor 
## data folder 
This folder contains the intermediate results of the computations performed.
This data is not stored in memory in order to ensure resilience in case of a temporary system failure. Not only that, but saving these files as jsons helps for increasing the lookup(KV) time, which is somewhat slow in relational databases.
The data saved in the jsons is always small and needs to be entirely read to perform the operations, as such this file-based storage seemed more appropriate then relying on SQL.
