import time
import board
import busio
from adafruit_mlx90640 import MLX90640

# Set up I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the MLX90640 sensor
mlx = MLX90640(i2c)
mlx.refresh_rate = MLX90640.RefreshRate.REFRESH_16_HZ

# Capture the temperature data from the sensor
def capture_data():
    frame = []
    mlx.getFrame(frame)  # This gets the 32x24 temperature data
    return frame

# Capture and display the data
while True:
    thermal_data = capture_data()
    print(thermal_data)  # Process or store this data as required
    time.sleep(1)  # Capture data every second
