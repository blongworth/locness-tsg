import serial
import logging
from typing import Generator, Optional

logger = logging.getLogger(__name__)

class SerialReader:
    def __init__(self, port: str, baudrate: int = 9600, timeout: int = 1):
        """Initialize serial connection with specified parameters."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None

    def connect(self) -> None:
        """Establish serial connection."""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            logger.info(f"Connected to serial port {self.port}")
        except serial.SerialException as e:
            logger.error(f"Failed to connect to serial port {self.port}: {str(e)}")
            raise

    def read_lines(self) -> Generator[str, None, None]:
        """
        Continuously read lines from serial port.
        Yields each line as it's received.
        """
        if not self.serial_conn:
            self.connect()
        
        while True:
            try:
                if self.serial_conn and self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line:
                        yield line
            except serial.SerialException as e:
                logger.error(f"Error reading from serial port: {str(e)}")
                self.close()
                raise
            except UnicodeDecodeError as e:
                logger.warning(f"Failed to decode line: {str(e)}")
                continue

    def close(self) -> None:
        """Close serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info(f"Closed connection to serial port {self.port}")