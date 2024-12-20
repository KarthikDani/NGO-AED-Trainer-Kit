from machine import Pin
import time

# Configure the GPIO pin for the LED (replace 2 with your GPIO pin number)
led = Pin(2, Pin.OUT)

# Toggle the LED in an infinite loop
while True:
    led.toggle()  # Toggle the LED state
    time.sleep(1)  # Wait for 1 second
