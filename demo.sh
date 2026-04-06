#!/bin/bash

echo "Starting USM server..."
python3 -m usm_server &

sleep 2

echo "Running test publisher..."
python3 testclient.py
