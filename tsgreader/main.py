from tsgreader.tsgparser import parse_tsg_line
from tsgreader.serialreader import SerialReader
import logging
import yaml
import csv
import sqlite3
from datetime import datetime, timezone


# Read the configuration file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access configuration values
TSG_PORT = config["stream"]["port"]
TSG_BAUD = config["stream"]["baudrate"]
LOGFILE = config["file"]["log"]
DATAFILE = config["file"]["data"]
DB_PATH = config["database"]["db"]
DB_TABLE = config["database"]["table"]

# Configure logging
logging.basicConfig(
    # filename=LOGFILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    handlers=[logging.FileHandler(LOGFILE), logging.StreamHandler()],
)

# Start logger
logger = logging.getLogger(__name__)

def write_to_database(parsed_line, db_path, table_name):
    """Write a single TSG data record to SQLite database."""
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Insert data into database
        cursor.execute(f'''
            INSERT INTO {table_name} 
            (datetime_utc, scan_no, cond, temp, salinity, hull_temp, time_elapsed, nmea_time, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            parsed_line.get('datetime_utc'),
            parsed_line.get('scan_no'),
            parsed_line.get('cond'),
            parsed_line.get('temp'),
            parsed_line.get('salinity'),
            parsed_line.get('hull_temp'),
            parsed_line.get('time_elapsed'),
            parsed_line.get('nmea_time'),
            parsed_line.get('latitude'),
            parsed_line.get('longitude')
        ))
        conn.commit()
    finally:
        conn.close()

def write_to_csv(parsed_line, datafile):
    """Write a single TSG data record to CSV file."""
    with open(datafile, 'a', newline='') as f:
        fieldnames = ['datetime_utc', 'scan_no', 'cond', 'temp', 'salinity', 'hull_temp',
                      'time_elapsed', 'nmea_time', 'latitude', 'longitude']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header if file is empty
        if f.tell() == 0:
            writer.writeheader()
        
        writer.writerow(parsed_line)

def main():
    
    # Create SerialReader instance
    reader = SerialReader(TSG_PORT, baudrate=TSG_BAUD)
    
    logger.info("Starting TSG data acquisition...")
    logger.info(f"Writing to CSV: {DATAFILE}")
    logger.info(f"Writing to database: {DB_PATH}")
    
    try:
        # Continuously read data and write to both CSV and database
        for line in reader.read_lines():
            try:
                parsed_line = parse_tsg_line(line)
                
                if parsed_line:  # Only write if parsing was successful
                    print(parsed_line)  # Display each record as it comes in
                    
                    # Write to CSV
                    try:
                        write_to_csv(parsed_line, DATAFILE)
                    except Exception as e:
                        logger.error(f"Error writing to CSV: {str(e)}")
                    
                    # Write to database
                    try:
                        write_to_database(parsed_line, DB_PATH, DB_TABLE)
                    except Exception as e:
                        logger.error(f"Error writing to database: {str(e)}")
                        
            except Exception as e:
                logger.error(f"Error parsing line: {line}. Error: {str(e)}")
                continue
                
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {str(e)}")
    finally:
        reader.close()
        logger.info("TSG data acquisition stopped.")
    

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)