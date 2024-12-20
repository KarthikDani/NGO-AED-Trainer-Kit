from machine import Pin
import time

# Define the GPIO pins connected to the rotary switch
# Replace these with your actual pin numbers
pins = [Pin(i, Pin.IN, Pin.PULL_UP) for i in [2, 3]]  # Example GPIO pins 2, 3

def read_rotary_switch():
    """
    Reads the state of the rotary switch and returns the position as an integer.
    The position is determined by the combination of the pin states.
    """
    state = [pin.value() for pin in pins]
    # Convert binary state to an integer position
    position = sum((1 << i) * val for i, val in enumerate(state))
    return position

def main():
    print("Rotary Switch Test Started")
    print("Rotate the switch to see the position...")
    
    try:
        while True:
            position = read_rotary_switch()
            print(f"Rotary Switch Position: {position}")
            time.sleep(0.5)  # Adjust the delay as needed
    except KeyboardInterrupt:
        print("Test ended.")

if __name__ == "__main__":
    main()
