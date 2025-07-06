from tsgreader.tsgparser import parse_tsg_line
from tsgreader.serialreader import SerialReader
import logging
import yaml
import csv


# Read the configuration file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access configuration values
TSG_PORT = config["stream"]["port"]
TSG_BAUD = config["stream"]["baudrate"]
LOGFILE = config["file"]["log"]
DATAFILE = config["file"]["data"]
DB_PATH = config["file"]["db"]

# TODO: write to database
# TODO: calculate salinity

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

def main():
    logging.basicConfig(level=logging.INFO)
    
    # Example usage of SerialReader
    reader = SerialReader(TSG_PORT, baudrate=TSG_BAUD)
    
    # Open CSV file and create DictWriter
    with open(DATAFILE, 'a', newline='') as f:
        fieldnames = ['scan_no', 'cond', 'temp', 'hull_temp', 
                     'time_elapsed', 'nmea_time', 'latitude', 'longitude']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header if file is empty
        if f.tell() == 0:
            writer.writeheader()
        
        try:
            for line in reader.read_lines():
                try:
                    parsed_line = parse_tsg_line(line)
                    print(parsed_line)  # Process each line as it comes in
                    if parsed_line:  # Only write if parsing was successful
                        writer.writerow(parsed_line)
                except Exception as e:
                    logger.error(f"Error parsing line: {line}. Error: {str(e)}")
                    continue
        except KeyboardInterrupt:
            reader.close()
        

if __name__ == "__main__":
    main()