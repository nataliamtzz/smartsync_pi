# SMARTSYNC: Heatmap Monitoring and Alert System

Hello there! This repo contains all the code I worked on over the past year for my senior design project: SMARTSYNC.

SMARTSYNC is a heatmap monitoring and alert system. The microcontroller used was a Raspberry Pi 4b, and the added peripherals were an MLX90640 Thermal Camera, a PIR Sensor, and a reset button. The system is designed to take readings from the thermal camera and process them on the microcontroller. Once they are processed, they will be pushed onto the DynamoBD database. From this, the website and application will display the data in a user-friendly way that is also interactive.

This code allows you to program a microcontroller (in this case, a raspberry pi 4b) to track data from a thermal camera, PIR sensor, and a reset button. 

The main file that gets executed is data_test.py
Other files are software & hardware tests

# Notes on how to install a virtual environment, and Python packages
https://www.notion.so/SmartSync-Senior-Design-Capstone-149a0d6cf0f0805da518d1f698169d1c?source=copy_link
