import pytest
import dashboard as db
import user_interface as ui
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
import pandas as pd

# UNIT TEST
def test_get_log():
    df = db.get_log()
    assert list(df.columns) == ['id', 'timestamp', 'month', 'op_unique_carrier', 'origin', 'dest',
       'dep_delay_new', 'dep_time_blk', 'taxi_out', 'cancelled', 'diverted',
       'crs_elapsed_time', 'distance', 'carrier_delay', 'weather_delay',
       'nas_delay', 'security_delay', 'late_aircraft_delay',
       'longest_add_gtime', 'div_airport_landings', 'weekend',
       'predicted_delay', 'true_delay', 'prediction_latency']
    assert len(df) > 0

def test_load_model():
    model = ui.load_model()
    assert model != None


# Integration tests should verify:
# Streamlit sends correct request payload
# Streamlit displays prediction returned by FastAPI

def test_streamlit_sends_correct_request_payload():

    at = AppTest.from_file("user_interface.py").run()

    # Select inputs
    at.selectbox[0].set_value(1)   # MONTH
    at.selectbox[1].set_value("American Airlines")
    at.selectbox[2].set_value("Denver International")
    at.selectbox[3].set_value("Los Angeles International")
    at.selectbox[4].set_value("No")
    at.selectbox[5].set_value("No")
    at.selectbox[6].set_value("No")
    at.selectbox[7].set_value("No")
    at.number_input[3].set_value(200)
    at.number_input[4].set_value(1200)
    at.selectbox[7].set_value("No")

    
    # Mock FastAPI response
    mock_response = type(
        "Response",
        (),
        {"json": lambda self: {"delay": 1}}
    )()

    with patch("user_interface.requests.post", return_value=mock_response) as mock_post:

        at.button[0].click().run()

        # Verify the request was sent to the correct endpoint
        mock_post.assert_called_once()

        args, kwargs = mock_post.call_args

        assert args[0] == "http://localhost:8000/predict"

        # Verify payload structure
        payload = kwargs["json"]

        assert "features" in payload
        assert "true_delay" in payload

        assert payload["features"]["MONTH"] == 1
        assert payload["features"]["OP_UNIQUE_CARRIER"] == "AA"
        assert payload["true_delay"] in [0.0, 1.0]