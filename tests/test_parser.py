import pytest
from tsgreader.tsgparser import parse_tsg_line
from datetime import datetime

def test_parse_valid_tsg_line():
    line = "1234 4.56 12.34 11.98 3600.5 1749519966 -42.1234 147.8901"
    result = parse_tsg_line(line)
    
    assert result['scan_no'] == 1234
    assert result['cond'] == 4.56
    assert result['temp'] == 12.34
    assert result['hull_temp'] == 11.98
    assert result['time_elapsed'] == 3600.5
    assert isinstance(result['nmea_time'], datetime)
    assert result['nmea_time'] == datetime.fromtimestamp(1749519966)  # Remove last 4 digits to match format
    assert result['latitude'] == -42.1234
    assert result['longitude'] == 147.8901

def test_parse_short_line():
    line = "1235 4.57 12.35 11.99"
    result = parse_tsg_line(line)
    
    assert result['scan_no'] == 1235
    assert result['cond'] == 4.57
    assert result['temp'] == 12.35
    assert result['hull_temp'] == 11.99
    assert result['time_elapsed'] == None
    assert result['nmea_time'] == None
    assert result['latitude'] == None
    assert result['longitude'] == None

def test_parse_invalid_field_count():
    line = "1236 4.58 12.36 11.97 3601.5"
    with pytest.raises(ValueError) as exc_info:
        parse_tsg_line(line)
    assert "Expected 4 or 8 fields" in str(exc_info.value)

def test_parse_invalid_numeric_data():
    line = "1237 bad 12.37 11.96 3603.5 000002.00 -42.1237 147.8904"
    with pytest.raises(ValueError) as exc_info:
        parse_tsg_line(line)
    assert "Error parsing TSG line" in str(exc_info.value)

def test_parse_file_data():
    data_file = "tests/data/2024_03_20_152p_HTcapture_SSout_notXML.TXT"
    with open(data_file) as f:
        lines = f.readlines()
        
    parsed_lines = []
    for line in lines:
        line = line.strip()
        if line:  # Skip empty lines
            try:
                result = parse_tsg_line(line)
                parsed_lines.append(result)
            except ValueError as e:
                pytest.fail(f"Failed to parse line: {line}\nError: {str(e)}")
    
    assert len(parsed_lines) > 0, "No lines were parsed from file"
    
    # Check that all parsed lines have the expected fields
    required_fields = ['scan_no', 'cond', 'temp', 'hull_temp', 
                      'time_elapsed', 'nmea_time', 'latitude', 'longitude']
    
    for parsed_line in parsed_lines:
        for field in required_fields:
            assert field in parsed_line, f"Missing field {field} in parsed line"
