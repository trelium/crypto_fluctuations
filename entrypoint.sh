#!/bin/bash
echo "Running first setup"
python3 /app/src/apihistoricprices.py
python3 /app/src/historicingestion.py
python3 /app/src/predictor.py

echo "Running the bot"
exec python3 src/servinglayer.py &
exec python3 src/apicurrentpercentages.py &
exec python3 src/notifier.py &
echo "End script"

while true; do
    currenttime=$(date +%H:%M)
    if [[ "$currenttime" == "00:01" ]]; then
        echo "Run"
        python3 /app/src/apihistoricprices.py
        python3 /app/src/historicingestion.py
        python3 /app/src/predictor.py
    else
        echo "Nothing"
    fi
    sleep 59.5
done