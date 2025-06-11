import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from tsgreader.main import main
import yaml

@pytest.fixture
def mock_config():
    return {
        "stream": {
            "port": "/dev/ttyUSB0",
            "baudrate": 9600
        },
        "file": {
            "log": "tsg.log",
            "data": "tsg_data.csv",
            "db": "tsg.db"
        }
    }

@pytest.fixture
def sample_tsg_data():
    data_file = Path(__file__).parent / 'data' / '2024_03_20_152p_HTcapture_SSout_notXML.TXT'
    with open(data_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def test_main_writes_to_csv(mock_config, sample_tsg_data):
    # Mock the config file reading
    mock_yaml = Mock()
    mock_yaml.safe_load.return_value = mock_config
    
    # Mock the SerialReader
    mock_reader = Mock()
    mock_reader.read_lines.return_value = iter(sample_tsg_data)
    mock_reader.close = Mock()
    
    # Mock the CSV file operations
    mock_csv_file = mock_open()
    
    with patch('builtins.open', mock_csv_file), \
         patch('yaml.safe_load', mock_yaml.safe_load), \
         patch('tsgreader.main.SerialReader', return_value=mock_reader), \
         patch('csv.DictWriter') as mock_csv_writer:
        
        # Run main until KeyboardInterrupt
        #with pytest.raises(KeyboardInterrupt):
        with patch('time.time', side_effect=[0, 1, 2]):  # Simulate time passing
            main()
        
        # Verify the serial port was closed
        #mock_reader.close.assert_called_once()
        
        # Verify data was written
        writer = mock_csv_writer.return_value
        assert writer.writerow.call_count == len(sample_tsg_data)

def test_main_handles_parser_error(mock_config):
    # Mock the config file reading
    mock_yaml = Mock()
    mock_yaml.safe_load.return_value = mock_config
    
    # Mock the SerialReader with invalid data
    mock_reader = Mock()
    mock_reader.read_lines.return_value = iter(["invalid data"])
    mock_reader.close = Mock()
    
    # Mock the CSV file operations
    mock_csv_file = mock_open()
    
    with patch('builtins.open', mock_csv_file), \
         patch('yaml.safe_load', mock_yaml.safe_load), \
         patch('tsgreader.main.SerialReader', return_value=mock_reader), \
         patch('csv.DictWriter') as mock_csv_writer:
        
        # Run main until KeyboardInterrupt
        #with pytest.raises(KeyboardInterrupt):
        with patch('time.time', side_effect=[0, 1, 2]):  # Simulate time passing
            main()
        
        # Verify no data was written for invalid input
        writer = mock_csv_writer.return_value
        assert writer.writerow.call_count == 0