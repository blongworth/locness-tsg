import random
import time
from datetime import datetime, timezone
import logging
import yaml
from tsgreader.tsgparser import conductivity_to_salinity
from tsgreader.main import write_to_csv, write_to_database

def generate_tsg_data():
    """
    Generate a single TSG data record as a dictionary.

    :return: A dictionary containing TSG data
    """
    salinity_range = (20.2, 20.3)
    temperature_range = (10.8, 10.9)
    pressure_range = (50, 250)
    latitude_range = (41.3166, 41.3167)
    longitude_range = (-72.0608, -72.0607)

    # Add current UTC timestamp as Unix timestamp
    current_utc = int(datetime.now(timezone.utc).timestamp())

    result = {
        "datetime_utc": current_utc,
        "scan_no": random.randint(1, 1000),
        "cond": round(random.uniform(*salinity_range), 4),
        "temp": round(random.uniform(*temperature_range), 4),
        "salinity": None,  # Placeholder for salinity
        "hull_temp": round(random.uniform(*temperature_range), 4),
        "time_elapsed": round(random.uniform(*pressure_range), 3),
        "nmea_time": int(datetime.now().timestamp()),
        "longitude": round(random.uniform(*longitude_range), 5),
        "latitude": round(random.uniform(*latitude_range), 5),
    }

    result['salinity'] = conductivity_to_salinity(result['cond'], result['temp'])
    return result



def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def main():

    # Configuration

    frequency = 1  # 1 data point per second
    config = load_config()
    file_path = config["file"]["data"]
    db_path = config["database"]["db"]
    table_name = config["database"]["table"]

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting continuous synthetic TSG data generation...")

    while True:
        try:
            # Generate data
            tsg_data = generate_tsg_data()
            logger.info(f"Generated TSG data: {tsg_data}")

            # Write to CSV
            write_to_csv(tsg_data, file_path)

            # Write to database
            write_to_database(tsg_data, db_path, table_name)

            time.sleep(1 / frequency)
        except KeyboardInterrupt:
            logger.info("Data generation interrupted by user. Stopping...")
            break
        except Exception as e:
            logger.error(f"Error during data generation or writing: {str(e)}")


if __name__ == "__main__":
    main()
