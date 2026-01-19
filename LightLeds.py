import serial
import time

# Set up the serial connections (one for each NodeMCU)
ser_nodemcu1 = serial.Serial('COM9', 115200)  # First NodeMCU (LEDs 1-32)
# ser_nodemcu2 = serial.Serial('COM10', 115200)  # Second NodeMCU (LEDs 33-64)

# Define a function to light up specific LEDs on a given NodeMCU
def light_up_leds_nodemcu1(leds):
    # Create a 32-bit integer with LEDs on (1) or off (0)
    led_state = 0
    for led in leds:
        if 1 <= led <= 32:  # Only control LEDs 1-32 for NodeMCU 1
            led_state |= (1 << (led - 1))

    # Send the integer as 4 bytes to NodeMCU 1
    ser_nodemcu1.write(led_state.to_bytes(4, byteorder='big'))
    ser_nodemcu1.flush()

# def light_up_leds_nodemcu2(leds):
#     # Create a 32-bit integer with LEDs on (1) or off (0)
#     led_state = 0
#     for led in leds:
#         if 33 <= led <= 64:  # Only control LEDs 33-64 for NodeMCU 2
#             led_state |= (1 << (led - 33))  # Adjust index for 33-64 range

#     # Send the integer as 4 bytes to NodeMCU 2
#     ser_nodemcu2.write(led_state.to_bytes(4, byteorder='big'))
#     ser_nodemcu2.flush()

# Example: Light up LED 7 on NodeMCU1 and LED 33 on NodeMCU2
light_up_leds_nodemcu1([7])   # Light up LED 7 on NodeMCU 1 (1-32)
#light_up_leds_nodemcu2([33])  # Light up LED 33 on NodeMCU 2 (33-64)

# Allow some time for the LEDs to stay lit
time.sleep(5)

# Turn off all LEDs on both NodeMCUs
light_up_leds_nodemcu1([])  # Turn off all LEDs on NodeMCU 1
#light_up_leds_nodemcu2([])  # Turn off all LEDs on NodeMCU 2

# Close the serial connections
ser_nodemcu1.close()
#ser_nodemcu2.close()