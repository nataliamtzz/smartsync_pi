import time
import board
import busio
import numpy as np
import adafruit_mlx90640
import warnings

warnings.filterwarnings("ignore", message="I2C frequency is not settable in python, ignoring!")

def main():
	#setup I2C connection
	i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
	#print("Initializing Thermal Cam ...")
	mlx = adafruit_mlx90640.MLX90640(i2c)
	mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
	#print("Thermal Cam initialized successfully.")

	frame =  np.zeros((24*32,)) #initialize the array for all 768 temp readings

	#while True:
	try:
		mlx.getFrame(frame) #capture frame from mlx90640
		average_temp_c = np.mean(frame)
		average_temp_f = (average_temp_c * 9.0 / 5.0) + 32.0
		print(f"{average_temp_f:.1f}F")
		time.sleep(1) #value based on how frequently you want updates
	except ValueError as e:
		print(f"Failed to read temp, retrying. Error: {str(e)}")
		time.sleep(0.5) #wait a bit before retrying to avoid flooding with requests
		#except KeyboardInterrupt:
		#	print("Exiting...")
		#	break
	except Exception as e:
		print(f"An unexpected error ocurred: {str(e)}")


if __name__ == "__main__":
	main()
