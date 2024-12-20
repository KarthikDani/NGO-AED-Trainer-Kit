import os
import time
from machine import Pin, SPI
from wavplayer import WavPlayer
from sdcard import SDCard

"""
Pico's GP10 (SCK) --> SD card's SCK
Pico's GP11 (MOSI) --> SD card's MOSI
Pico's GP8 (MISO) --> SD card's MISO
Pico's GP13 --> SD card's CS
"""

spi = SPI(
    1,
    baudrate=1_000_000,  # this has no effect on spi bus speed to SD Card
    polarity=0,
    phase=0,
    bits=8,
    firstbit=machine.SPI.MSB,
#     sck=Pin(14),
#     mosi=Pin(15),
#     miso=Pin(12),
)

# ======= SD CARD CONFIGURATION =======
sd = SDCard(spi, Pin(13))
#sd.init_spi(25_000_000)  # increase SPI bus speed to SD card
os.mount(sd, "/sd")
# ======= SD CARD CONFIGURATION =======

# ======= I2S CONFIGURATION =======
SCK_PIN = 16
WS_PIN = 17
SD_PIN = 18
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 40000
# ======= I2S CONFIGURATION =======

wp = WavPlayer(
    id=I2S_ID,
    sck_pin=Pin(SCK_PIN),
    ws_pin=Pin(WS_PIN),
    sd_pin=Pin(SD_PIN),
    ibuf=BUFFER_LENGTH_IN_BYTES,
)

wp.play("music-16k-16bits-mono.wav", loop=False)
# wait until the entire WAV file has been played
while wp.isplaying() == True:
    # other actions can be done inside this loop during playback
    pass

wp.play("Hindi/music-16k-16bits-mono.wav", loop=False)
time.sleep(10)  # play for 10 seconds

wp.pause()

time.sleep(5)  # pause playback for 5 seconds
wp.resume()  # continue playing to the end of the WAV file
