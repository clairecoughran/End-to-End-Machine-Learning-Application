#!/bin/bash

streamlit run user_interface.py \
    --server.address=0.0.0.0 \
    --server.port=8501 &

streamlit run dashboard.py \
    --server.address=0.0.0.0 \
    --server.port=8502 &

wait

