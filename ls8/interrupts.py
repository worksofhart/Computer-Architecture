import threading
import time
import sys
from kbhit import KBHit

# Register name constants
IM = 5  # Interrupt Mask, reg R5
IS = 6  # Interrupt Status, reg R6

# Masks for isolating IS bits
TIMER = 0b00000001
KEYBOARD = 0b00000010


class Interrupts():
    """
    Set up a thread to manage interrupt sources
    - Keyboard is polled update_interval times per second and interrupt
        is triggered on keypress
    - Timer interrupt updates once per second
    """

    DONE = False  # Set to True to kill thread
    ENABLED = True  # After being set False, remains set until serviced
    TICKS = 0  # Clock TICKS update_interval times per second

    kb = KBHit()  # Scan for key presses

    def __init__(self, regs, update_interval=60):
        self.update_interval = update_interval
        self.delay = 1 / update_interval
        self.regs = regs  # Registers from CPU
        self.keypressed = 0b00000000  # Stores current keypress

    def interrupts_task(self):
        while not self.DONE:
            # Read currently pressed key if any. If ESC key is pressed, exit
            self.keypressed = ord(self.kb.getch()) if self.kb.kbhit() else 0
            if self.keypressed and self.keypressed == 27:
                self.DONE = True
                print()
                sys.exit()

            if self.regs[IM] and self.ENABLED:
                # Keyboard interrupt triggered as many as update_interval
                # times per second
                if self.keypressed:
                    # If a key is in the buffer, set IS bit
                    self.regs[IS] |= KEYBOARD
                # Timer interrupt triggered once per second
                if not self.TICKS:
                    # Set Timer status bit when TICKS = 0
                    self.regs[IS] |= TIMER

            # Wait specified time before processing interrupts again
            time.sleep(self.delay)

            # Advance time counter. When TICKS == update_interval, reset to 0
            self.TICKS = (self.TICKS + 1) % self.update_interval

    def __enter__(self):
        # Start interrupts thread
        threading.Thread(target=self.interrupts_task).start()
        return self

    def __exit__(self, exception, value, tb):
        if exception is not None:
            return False

    def stop(self):
        self.DONE = True
