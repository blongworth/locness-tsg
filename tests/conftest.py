import pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def check_test_data():
    data_file = Path(__file__).parent / 'data' / '2024_03_20_152p_HTcapture_SSout_notXML.TXT'
    if not data_file.exists():
        raise FileNotFoundError(
            f"Test data file not found: {data_file}\n"
            "Please ensure the TSG data file is placed in the tests/data directory"
        )