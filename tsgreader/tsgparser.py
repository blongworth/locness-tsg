from datetime import datetime

def parse_tsg_line(line: str) -> dict:
    """
    Parse a single line of TSG data.
    
    Args:
        line (str): A whitespace-delimited string containing TSG measurements
        
    Returns:
        dict: Parsed TSG data. If line has only 4 fields, last 4 fields will be None
        
    Example formats:
        scan_no cond temp hull_temp time_elapsed nmea_time latitude longitude
        scan_no cond temp hull_temp
    """
    try:
        fields = line.strip().split()
        if len(fields) not in [4, 8]:
            raise ValueError(f"Expected 4 or 8 fields, got {len(fields)}")
            
        result = {
            'scan_no': int(fields[0]),
            'cond': float(fields[1]),
            'temp': float(fields[2]),
            'hull_temp': float(fields[3]),
            'time_elapsed': None,
            'nmea_time': None,
            'latitude': None,
            'longitude': None
        }
        
        if len(fields) == 8:
            result.update({
                'time_elapsed': float(fields[4]),
                'nmea_time': datetime.fromtimestamp(int(fields[5])),
                'latitude': float(fields[6]),
                'longitude': float(fields[7])
            })
            
        return result
        
    except (ValueError, IndexError) as e:
        raise ValueError(f"Error parsing TSG line: {str(e)}") from e