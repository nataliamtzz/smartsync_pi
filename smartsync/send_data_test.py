import time
from datetime import datetime
import board
import busio
import boto3
import numpy as np
import adafruit_mlx90640
import json
import warnings

warnings.filterwarnings("ignore", message="I2C frequency is not settable in python, ignoring!")

#from decimal import Decimal

#from adafruit_mlx90640 import MLX90640

#initialize
#i2c = busio.I2C(board.SCL, board.SDA)
#mlx = adafruit_mlx90640.MLX90640(i2c)
#mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

#mlx.refresh_rate = MLX90640.MLX90640.REFRESH_2_HZ

dynamodb = boto3.resource(
	'dynamodb',
	aws_access_key_id='...',
	aws_secret_access_key='...',
	region_name='...'
)
table = dynamodb.Table('SmartSync')

def capture_data():
	#setup I2C connection
	i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
	#print("Initializing Thermal Cam ...")
	mlx = adafruit_mlx90640.MLX90640(i2c)
	mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
	#print("Thermal Cam initialized successfully.")

	frame =  np.zeros((24*32,)) #initialize the array for all 768 temp readings

	try:
		mlx.getFrame(frame) #capture frame from mlx90640
		max_temp = np.max(frame)
		Temperature = (max_temp * 9.0 / 5.0) + 32.0
		print(f"{Temperature:.1f} F")
		time.sleep(1) #value based on how frequently you want updates
		return Temperature
	except ValueError as e:
		print(f"Failed to read temp, retrying. Error: {str(e)}")
		time.sleep(0.5) 
	except Exception as e:
		print(f"An unexpected error ocurred: {str(e)}")

def upload_to_dynamodb(Temperature):
	if Temperature is None:
		return

	TimeStamp = datetime.now().strftime("%I:%M %p")
	Date = datetime.now().strftime("%m/%d/%Y")
	Room = datetime.now().strftime("%m-%d-%Y")

	item = {
		'Room' : f'F260-{Room}',
		'Timestamp' : TimeStamp,
		'Date' : Date,
		'Location' : 'F260',
		'Temperature' : Temperature
	}
	try:
		response = table.put_item(Item=item)
		print(f"Uploaded data at {TimeStamp}:\n", response)
	except Exception as e:
		print(f"Failed to upload data: {e.response['Error']['Message']}")
	
def main():
		Temperature = capture_data()
		upload_to_dynamodb(Temperature)
		
if __name__ == "__main__":
		main()

while True:
	thermal_data = capture_data()
	upload_to_dynamodb(thermal_data)
	time.sleep(5) #every 5 seconds
	time.sleep(5) #every 5 seconds
