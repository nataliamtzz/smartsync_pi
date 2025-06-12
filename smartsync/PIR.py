from gpiozero.pins.rpigpio import RPiGPIOFactory
from gpiozero import MotionSensor
from signal import pause
from datetime import datetime

factory = RPiGPIOFactory()

pir = MotionSensor(4, pin_factory = factory)

def motion_function():
	current_time = datetime.now().strftime("%I:%M %p")
	print(f"Motion Detected at {current_time}")

def no_motion_function():
	current_time = datetime.now().strftime("%I:%M %p")
	print(f"Motion stopped at {current_time}")

pir.when_motion = motion_function
pir.when_no_motion = no_motion_function

try:
	pause()
except KeyboardInterrupt:
	print("Program termindated by user")
