import time
from datetime import datetime
import board
import busio
import boto3
import numpy as np
import adafruit_mlx90640
import json
import warnings
import RPi.GPIO as GPIO
from decimal import Decimal
import botocore
import subprocess

# Setup for PIR Sensor
PIR_PIN = 4
BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

warnings.filterwarnings("ignore", message="I2C frequency is not settable in python, ignoring!")

# Initialize DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
lambda_client = boto3.client('lambda', region_name='us-east-1')
table = dynamodb.Table('SmartSync')

def trigger_lambda_error(error_message):
    try:
        payload = json.dumps({"error": error_message})
        response = lambda_client.invoke(
            FunctionName='ErrorLogs',
            InvocationType='Event',
            Payload=payload
        )
        print("Error sent to Lambda for notification.")
    except Exception as e:
        print(f"Failed to invoke Lambda: {str(e)}")

def capture_data():
    try:
        # Setup I2C connection
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        mlx = adafruit_mlx90640.MLX90640(i2c)
        mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
    except Exception as e:
        error_message = f"Sensor read error: {str(e)}"
        print(error_message)
        trigger_lambda_error(json.dumps({"camera": error_message}))
        return None

    frame = np.zeros((24*32,))
    try:
        mlx.getFrame(frame)
        temp_c = np.max(frame)
        Temperature = (temp_c * 9.0 / 5.0) + 32.0
        Temperature = round(Temperature, 1)
        print(f"{Temperature:.1f}F")
        return Temperature
    except Exception as e:
        error_message = f"Sensor read error: {str(e)}"
        print(error_message)
        trigger_lambda_error(json.dumps({"camera": error_message}))
        return None

def upload_to_dynamodb(Temperature):
    if Temperature is None:
        print("Temperature value is None, skipping upload.")
        return
    
    try:
        Temperature = Decimal(str(Temperature))
        TimeStamp = datetime.now().strftime("%I:%M %p")
        Date = datetime.now().strftime("%m/%d/%Y")
        Room = "F260"

        item = {
            'Room': f'F260-{Date}',
            'Timestamp': TimeStamp,
            'Date': Date,
            'Location': Room,
            'Temperature': f'{Temperature:.1f} F'
        }

        response = table.put_item(Item=item)
        print(f"Uploaded data at {TimeStamp}:\n", response)

    except Exception as e:
        print(f"Unexpected Error: {e}")

def run_button_script():
    print("Button pressed! Running button.py in background...")
    try:
        subprocess.Popen(["python3", "button.py"])
        print("Continuing to monitor motion and button...")
    except Exception as e:
        print(f"Error running button.py: {e}")


def main():
    print("Wait... Thermal camera detecting motion.")
    try:
        while True:
            # Check for motion
            if GPIO.input(PIR_PIN):
                print("Motion Detected! Capturing thermal data...")
                Temperature = capture_data()
                upload_to_dynamodb(Temperature)
                time.sleep(1)
            else:
                print("Waiting for motion...")

            # Check for button press
            if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                run_button_script()

            time.sleep(2)  # Adjust based on desired responsiveness

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
