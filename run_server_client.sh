#!/bin/bash

PORT=65432
lsof -ti:$PORT | xargs kill

# Start the server in the background
python3 -m server_client server &

# Allow some time for the server to initialize
sleep 2

# Run both client commands in the background
python3 -m server_client client &
python3 -m server_client client &

# Wait for all background jobs to finish
wait
