import os
import time
from machine import Pin, SPI
from wavplayer import WavPlayer
from sdcard import SDCard

# Pin assignments for rotary switch (assuming pins 5 to 9 for the switch)
ROTARY_PINS = [Pin(2, Pin.IN, Pin.PULL_UP),  # Hindi
               Pin(3, Pin.IN, Pin.PULL_UP),  # Kannada
               Pin(4, Pin.IN, Pin.PULL_UP),  # Telugu
               Pin(5, Pin.IN, Pin.PULL_UP),  # Tamil
               Pin(6, Pin.IN, Pin.PULL_UP),  # Malayalam
               Pin(7, Pin.IN, Pin.PULL_UP),  # English
               ]

BUTTON_PLAY_PIN = Pin(14, Pin.IN, Pin.PULL_UP)  # Play button pin
BUTTON_PAUSE_TOGGLE_PIN = Pin(15, Pin.IN, Pin.PULL_UP)  # Pause/Play toggle button pin

LED_PINS = [Pin(19, Pin.OUT),
            Pin(20, Pin.OUT),
            Pin(21, Pin.OUT)]

# SPI configuration for SD card
spi = SPI(
    1,
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    bits=8,
    firstbit=machine.SPI.MSB,
)

# Initialize SD card
sd = SDCard(spi, Pin(13))
os.mount(sd, "/sd")

# Initialize I2S for audio playback
SCK_PIN = 16
WS_PIN = 17
SD_PIN = 18
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 40_000

# Interrupts controlled Flags
to_stop = False
to_change_file_index_and_play = False


wp = WavPlayer(
    id=I2S_ID,
    sck_pin=Pin(SCK_PIN),
    ws_pin=Pin(WS_PIN),
    sd_pin=Pin(SD_PIN),
    ibuf=BUFFER_LENGTH_IN_BYTES,
)

# Function to check if a path is a directory using os.stat
def is_directory(path):
    try:
        return os.stat(path)[0] & 0x4000  # Check if the mode indicates it's a directory
    except OSError:
        return False

# Get list of language directories in SD card
language_dirs = [d for d in os.listdir('/sd') if is_directory(f'/sd/{d}') and not d.startswith('.')]

# Initialize variables
current_language_index = 0
current_file_index = -1
last_play_button_press_time = 0  # Track the last time the play button was pressed
last_toggle_button_press_time = 0  # Track the last time the pause/play toggle button was pressed
current_file_playing = ""

def get_wav_files(language):
    """Get list of .wav files in a directory."""
    return [f for f in os.listdir(f"/sd/{language}") if f.endswith(".wav")]

def play_wav_file(file_name):
    """Play the selected wav file."""
    global current_file_playing
    current_file_playing = file_name
    print(f"Playing: {current_file_playing}")
    wp.play(f"{file_name}", loop=False)

def handle_file_index_and_play():
    global current_file_index, language_dirs
    wav_files = get_wav_files(language_dirs[current_language_index])
    
    if current_file_index < len(wav_files) - 1:
        current_file_index += 1
        play_wav_file(wav_files[current_file_index])
        
    else:
        current_file_index = 0  # Loop back to the first file
        play_wav_file(wav_files[current_file_index])

def on_play_button_press(pin):
    """Interrupt service routine to handle play button press with debounce."""
    global current_file_index, last_play_button_press_time, to_change_file_index_and_play, to_stop

    current_time = time.ticks_ms()
    # If the button was pressed less than 300ms ago, ignore it (debounce)
    if time.ticks_diff(current_time, last_play_button_press_time) < 300:
        return

    last_play_button_press_time = current_time

    if wp.isplaying():
        to_stop = True

    to_change_file_index_and_play = True

def turn_on_led(pin):
    for led in LED_PINS:
        led.value(0)
    pin.value(1)

def on_toggle_button_press(pin):
    """Interrupt service routine to handle pause/play toggle button press with debounce."""
    global last_toggle_button_press_time, to_stop

    current_time = time.ticks_ms()
    # If the button was pressed less than 300ms ago, ignore it (debounce)
    if time.ticks_diff(current_time, last_toggle_button_press_time) < 300:
        return

    last_toggle_button_press_time = current_time

    if wp.isplaying():
        to_stop = True

# Function to handle language selection via rotary switch interrupts
def on_rotary_switch_change(pin):
    global current_language_index, current_file_index, to_stop
    to_stop = True
    for i, rotary_pin in enumerate(ROTARY_PINS):
        if not rotary_pin.value():  # Active-low check
            current_language_index = i
            print(f"Language changed to: {language_dirs[current_language_index]}")
            current_file_index = -1  # Reset file index when language changes
            break
    
# Attach the interrupt to the buttons
BUTTON_PLAY_PIN.irq(trigger=Pin.IRQ_RISING, handler=on_play_button_press)
BUTTON_PAUSE_TOGGLE_PIN.irq(trigger=Pin.IRQ_RISING, handler=on_toggle_button_press)

# Attach interrupts to rotary switch pins
for pin in ROTARY_PINS:
    pin.irq(trigger=Pin.IRQ_RISING, handler=on_rotary_switch_change)

on_rotary_switch_change(BUTTON_PLAY_PIN)

# Main loop to control rotary switch
# while True:
# #     # Check rotary switch to select language directory
# #     for i, pin in enumerate(ROTARY_PINS):
# #         if not pin.value():  # Detect which pin is low (rotary switch positions are active low)
# #             current_language_index = i
# #             print(f"Selected Language: {language_dirs[current_language_index]} | File: {current_file_index} | Name: {current_file_playing}")
# #             break
#     time.sleep_ms(150)  # Delay to debounce rotary switch 

while True:
    if to_stop:
        wp.stop()
        to_stop = False
    
    if to_change_file_index_and_play:
        handle_file_index_and_play()
        to_change_file_index_and_play = False
    
    if current_file_index < 0:
        turn_on_led(LED_PINS[current_file_index + 1])
    else:
        turn_on_led(LED_PINS[current_file_index])

    print(f"current_file_index: {current_file_index} | current_langauge_index: {current_language_index}")
    time.sleep_ms(10)