import threading
import requests
import time
import sys
from kbhit import KBHit
from random import uniform

# Register name constants
IM = 5  # Interrupt Mask, reg R5
IS = 6  # Interrupt Status, reg R6

# Masks for isolating IS bits
TIMER = 0b00000001
KEYBOARD = 0b00000010


class Interrupts():
    """
    Set up a thread to manage interrupt sources
    - Keyboard is polled update_interval times per second and interrupt is triggered on keypress
    - Timer interrupt updates once per second
    """
    active = True  # Set to false to kill thread
    disabled = False  # After being set True, remains set until serviced
    ticks = 0  # Clock ticks update_interval times per second
    kb = KBHit()  # Scan for key presses

    def __init__(self, regs, update_interval=60):
        self.update_interval = update_interval
        self.delay = 1 / update_interval
        self.timer_enabled = False
        self.regs = regs  # Registers from CPU
        self.keypressed = 0b00000000  # Stores current keypress

    def interrupts_task(self):
        while self.active:
            if self.regs[IM] and not self.disabled:
                # Keyboard interrupt triggered as many as update_interval times per second
                self.keypressed = self.kb.getch() if self.kb.kbhit() else 0
                # If a key is in the buffer and it's not Esc
                if self.keypressed and ord(key) != 27:
                    self.regs[IS] |= KEYBOARD
                elif ord(self.keypressed) == 27:
                    self.active = False
                    sys.exit()
                # Timer interrupt triggered once per second
                if not self.ticks:
                    self.regs[IS] |= TIMER  # Set Timer status bit

            time.sleep(self.delay)
            self.ticks = (self.ticks + 1) % self.update_interval

    def __enter__(self):
        try:
            threading.Thread(target=self.interrupts_task).start()
        except:  # Handle exceptions
            raise Exception("Could not initialize interrupts thread")
        return self

    def __exit__(self, exception, value, tb):
        if exception is not None:
            return False

    def stop(self):
        self.active = False
