import time,sys,spidev
import gaugette.ssd1306

RESET_PIN = 0 #15
DC_PIN    = 1 #16

led = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
led.begin()
#led.invert_display()
led.clear_display()
led.display()
