#!/bin/bash

docker build . --tag titan:$(date +%F) --tag titan:latest
