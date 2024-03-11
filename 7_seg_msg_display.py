import RPi.GPIO as GPIO
import time

# Pin Definitions for Shift Register 1
SDI_A = 11
RCLK_A = 12
SRCLK_A = 13

# Pin Definitions for Shift Register 2
SDI_B = 15
RCLK_B = 16
SRCLK_B = 18

# Define segment codes for alphabets A-Z (common anode)
alphaSegCode = [
    0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71, 0x6F, 0x74, 0x04, 0x0E,
    0x1C, 0x38, 0x55, 0x54, 0x5C, 0x73, 0x67, 0x50, 0x6D, 0x78,
    0x3E, 0x1C, 0x55, 0x6E, 0x6E  # Adjusted to include necessary codes for A-Z
]

# Shift Register Constants
SHIFT_REGISTERS = {
    'A': {'SDI': SDI_A, 'RCLK': RCLK_A, 'SRCLK': SRCLK_A},
    'B': {'SDI': SDI_B, 'RCLK': RCLK_B, 'SRCLK': SRCLK_B}
}

# Time Constants
TRANSITION_DELAY = 0.2
CHARACTER_DELAY = 0.2

def print_msg():
    print('Program is running...')
    print('Please press Ctrl+C to end the program...')

def setup():
    GPIO.setmode(GPIO.BOARD)  # Number GPIOs by physical location
    for pins in SHIFT_REGISTERS.values():
        for pin in pins.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

def hc595_shift(dat, reg):
    pins = SHIFT_REGISTERS[reg]
    for bit in range(7, -1, -1):
        GPIO.output(pins['SDI'], not ((dat >> bit) & 0x01))  # Invert logic for common anode
        GPIO.output(pins['SRCLK'], GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(pins['SRCLK'], GPIO.LOW)
    GPIO.output(pins['RCLK'], GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(pins['RCLK'], GPIO.LOW)

def display_alphabet(alpha, display):
    alpha_index = ord(alpha.upper()) - ord('A')
    if 0 <= alpha_index < len(alphaSegCode):
        hc595_shift(alphaSegCode[alpha_index], display)
    else:
        hc595_shift(0x00, display)

def custom_message():
    message = "hi you did good job "
    
    for i, char in enumerate(message[:-1]):
        if char.isalpha():
            display_alphabet(char, 'B')  # Display current alphabet on the second display
            # No need to turn off the first display

            time.sleep(TRANSITION_DELAY)  # Small delay to observe the transition

            next_char = message[i + 1]
            display_alphabet(next_char, 'B')  # Display the next alphabet on the second display

            display_alphabet(char, 'A')  # Display current alphabet on the first display
            # No need to turn off the second display

            time.sleep(CHARACTER_DELAY)  # Small delay between characters
        elif char.isspace():
            hc595_shift(0x00, 'A')  # Turn off the first display for spaces
            hc595_shift(0x00, 'B')  # Turn off the second display for spaces
            time.sleep(CHARACTER_DELAY)  # Small delay between words

    # Display an additional space after the last 'B'
    hc595_shift(0x00, 'A')  # Turn off the first display for the additional space
    hc595_shift(0x00, 'B')  # Turn off the second display for the additional space
    time.sleep(CHARACTER_DELAY)  # Small delay between characters

    # After displaying the entire message, add a longer delay before restarting
    time.sleep(2 * CHARACTER_DELAY)


def loop():
    print_msg()
    while True:
        custom_message()

def destroy():
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    custom_message()  # Initial display for a smooth start
    loop()
