import time
from datetime import datetime
import board
import busio
import boto3
import numpy as np
import adafruit_mlx90640
import warnings
import RPi.GPIO as GPIO
from decimal import Decimal

# Setup for PIR Sensor
PIR_PIN = 4  # GPIO pin for the PIR sensor
# Setup for button
BUTTON_PIN = 17  # Change to a different GPIO pin if needed

# Initialize GPIO
GPIO.setmode(GPIO.BCM)  # Using Broadcom pin numbering
GPIO.setup(PIR_PIN, GPIO.IN)  # Set PIR_PIN as input
GPIO.setwarnings(False)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

warnings.filterwarnings("ignore", message="I2C frequency is not settable in python, ignoring!")

# Initialize DynamoDB connection
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id='AKIARHJJNDFNZC2VBOGU',
    aws_secret_access_key='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',
    region_name='us-east-1'
)
table = dynamodb.Table('SmartSync')
table2 = dynamodb.Table('ResetRecords')

def capture_data():
    # Setup I2C connection
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
    mlx = adafruit_mlx90640.MLX90640(i2c)
    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

    frame = np.zeros((24*32,))  # Initialize the array for all 768 temp readings

    try:
        mlx.getFrame(frame)  # Capture frame from mlx90640
        temp_c = np.max(frame)
        Temperature = (temp_c * 9.0 / 5.0) + 32.0
        Temperature = round(Temperature, 1)
        
        print(f"{Temperature:.1f}F")
        return Temperature
    except ValueError as e:
        print(f"Failed to read temp, retrying. Error: {str(e)}")
        time.sleep(0.15)  # Wait a bit before retrying to avoid flooding with requests
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def upload_to_dynamodb(Temperature):
    if Temperature is None:
        return

    # Convert Temperature to Decimal
    Temperature = Decimal(str(Temperature))

    TimeStamp = datetime.now().strftime("%I:%M %p")
    Date = datetime.now().strftime("%m/%d/%Y")
    Room = datetime.now().strftime("%m-%d-%Y")

    item = {
        'Room': f'F260-{Room}',
        'Timestamp': TimeStamp,
        'Date': Date,
        'Location': 'F260',
        'Temperature': f'{Temperature:.1f} F'
    }

    try:
        response = table.put_item(Item=item)
        print(f"Uploaded data at {TimeStamp}:\n", response)
    except Exception as e:
        print(f"Failed to upload data: {str(e)}")

def reset():
    TimeStamp = datetime.now().strftime("%I:%M %p")
    item = {
        "Room": "F260",
        "Reset": "True",
        "Timestamp": TimeStamp
    }
    try:
        response = table2.put_item(Item=item)
        print("Data successfully written to DynamoDB:", response)
    except Exception as e:
        print(f"Error writing to DynamoDB: {e}")

def main():
    print("Wait ... ;), thermal camera detecting: ")
    prev_state = GPIO.input(BUTTON_PIN)  # Ensure proper initial state

    while True:
        # Button check
        curr_state = GPIO.input(BUTTON_PIN)
        if curr_state == GPIO.HIGH and prev_state == GPIO.LOW:
            print("Button Press Detected! Uploading reset to database...")
            reset()
            time.sleep(0.2)  # Debouncing
        prev_state = curr_state
        
        # PIR Sensor Check
        if GPIO.input(PIR_PIN):
            print("Motion detected! Capturing thermal data...")
            Temperature = capture_data()
            upload_to_dynamodb(Temperature)
            time.sleep(1)
        else:
            print("Waiting for motion...")
            time.sleep(2.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        GPIO.cleanup()  # Clean up GPIO pins on exit
