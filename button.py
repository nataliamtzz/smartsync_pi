##################################################################################
import RPi.GPIO as GPIO
import time
import boto3

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialize DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('ResetRecords')

def upload_to_dynamodb():
    item = {
        "Room": "F260",
        "Reset": "True"
    }
    try:
        response = table.put_item(Item=item)
        print("Data successfully written to DynamoDB:", response)
    except Exception as e:
        print(f"Error writing to DynamoDB: {e}")

def monitor_button():
    previous_state = GPIO.LOW
    print("Waiting for button press...")

    while True:
        current_state = GPIO.input(17)
        if current_state == GPIO.HIGH and previous_state == GPIO.LOW:
            print("Button was pushed! Uploading to database...")
            upload_to_dynamodb()
            time.sleep(0.2)  # Prevents accidental multiple uploads
        previous_state = current_state

if __name__ == "__main__":
    try:
        monitor_button()
    except KeyboardInterrupt:
        print("\nExiting...")
        GPIO.cleanup()
