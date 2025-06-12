import board
import busio
import adafruit_mlx90640
import warnings

#supress specific benign warning
warnings.filterwarnings("ignore", category=RuntimeWarning, message="I2C Frequency is not settable in Python, ignoring!")

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
mlx = adafruit_mlx90640.MLX90640(i2c)

print("MLX90640 Device Found!")
