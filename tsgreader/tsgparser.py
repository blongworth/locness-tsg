from datetime import datetime, timezone
import gsw

def parse_coordinate(coord_str: str, coord_type: str) -> float:
    """
    Parse coordinate string in format "DD MM.MMMM N/S/E/W" to decimal degrees.
    
    Args:
        coord_str (str): Coordinate string like "41 31.4341 N" or "070 40.3335 W"
        coord_type (str): 'lat' for latitude or 'lon' for longitude
        
    Returns:
        float: Coordinate in decimal degrees
    """
    parts = coord_str.split()
    if len(parts) != 3:
        raise ValueError(f"Invalid coordinate format: {coord_str}")
    
    degrees = float(parts[0])
    minutes = float(parts[1])
    direction = parts[2]
    
    decimal_degrees = degrees + minutes / 60.0
    
    # Apply sign based on direction
    if direction in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    
    return decimal_degrees

def parse_datetime(hms_str: str, dmy_str: str) -> datetime:
    """
    Parse time and date strings to datetime object.
    
    Args:
        hms_str (str): Time string in HHMMSS format
        dmy_str (str): Date string in DDMMYY format
        
    Returns:
        datetime: Parsed datetime object
    """
    if len(hms_str) != 6 or len(dmy_str) != 6:
        raise ValueError(f"Invalid time/date format: {hms_str}, {dmy_str}")
    
    hour = int(hms_str[:2])
    minute = int(hms_str[2:4])
    second = int(hms_str[4:6])
    
    day = int(dmy_str[:2])
    month = int(dmy_str[2:4])
    year = 2000 + int(dmy_str[4:6])  # Assume 20XX
    
    return datetime(year, month, day, hour, minute, second)

def parse_tsg_line(line: str) -> dict:
    """
    Parse a single line of TSG data in key-value format.

    Args:
        line (str): A comma-delimited string containing TSG measurements in key=value format

    Returns:
        dict: Parsed TSG data

    Example format:
        t1= 25.5397, c1= 0.03668, s=  0.1750, t2= 21.9663, lat=41 31.4341 N, lon=070 40.3335 W, hms=210916, dmy=110825
    """
    try:
        # Parse key-value pairs
        pairs = [pair.strip() for pair in line.split(',')]
        data_dict = {}

        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                data_dict[key.strip()] = value.strip()

        # Validate that we have at least the basic required fields
        required_fields = ['t1', 'c1', 't2', 's']
        missing_fields = [field for field in required_fields if field not in data_dict]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Add current UTC timestamp as Unix timestamp
        current_utc = int(datetime.now(timezone.utc).timestamp())

        # Parse coordinates
        latitude = parse_coordinate(data_dict.get('lat', ''), 'lat') if 'lat' in data_dict else None
        longitude = parse_coordinate(data_dict.get('lon', ''), 'lon') if 'lon' in data_dict else None

        # Parse date/time
        nmea_time = None
        if 'hms' in data_dict and 'dmy' in data_dict:
            nmea_time = parse_datetime(data_dict['hms'], data_dict['dmy'])

        result = {
            'datetime_utc': current_utc,
            'scan_no': None,  # Not provided in new format
            'cond': float(data_dict.get('c1', 0)),
            'temp': float(data_dict.get('t1', 0)),
            'hull_temp': float(data_dict.get('t2', 0)),
            'salinity': float(data_dict.get('s', 0)),
            'time_elapsed': None,  # Not provided in new format
            'nmea_time': nmea_time,
            'latitude': latitude,
            'longitude': longitude
        }

        return result

    except (ValueError, IndexError) as e:
        raise ValueError(f"Error parsing TSG line: {str(e)}") from e

def conductivity_to_salinity(cond: float, temp: float, pressure: float = 0) -> float:
    """
    Convert conductivity to salinity in PSU using the GSW toolkit.

    Args:
        cond (float): Conductivity in S/m.
        temp (float): Temperature in degrees Celsius.
        pressure (float): Pressure in dbar (default is 0).

    Returns:
        float: Salinity in PSU.

    Raises:
        ValueError: If cond, temp, or pressure are negative.
    """
    if cond < 0 or temp < 0 or pressure < 0:
        raise ValueError("cond, temp, and pressure must be non-negative values.")
    return gsw.conversions.SP_from_C(cond, temp, pressure)