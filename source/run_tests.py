#!/usr/bin/env python
"""
This test suite runs on the Raspberry Pi and tests RPIO inside out.
"""
import os
import time
import unittest
import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)

import RPIO

GPIO_IN = 14
GPIO_OUT = 17


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        RPIO.setwarnings(False)

    def test1_version(self):
        logging.info("Version: %s (%s)", RPIO.VERSION, RPIO.VERSION_GPIO)

    def test2_rpio_cmd(self):
        logging.info("Running `sudo rpio --version`...")
        #os.system("sudo python rpio --version")
        logging.info("Running `sudo rpio -I`...")
        #os.system("sudo python rpio -I")
        logging.info("Running `sudo rpio -i 5,%s,%s`...", GPIO_IN, GPIO_OUT)
        #os.system("sudo python rpio -i 5,%s,%s" % (GPIO_IN, GPIO_OUT)

    def test3_input(self):
        with self.assertRaises(RPIO.InvalidChannelException):
            # 5 is not a valid gpio
            RPIO.setup(5, RPIO.IN)
        with self.assertRaises(RPIO.InvalidChannelException):
            # 5 is not a valid gpio
            RPIO.setup(0, RPIO.IN)
        with self.assertRaises(RPIO.InvalidChannelException):
            # 5 is not a valid gpio
            RPIO.setup(32, RPIO.IN)

        RPIO.setup(GPIO_IN, RPIO.IN)
        logging.info(" ")
        logging.info("--------------------------------------")
        logging.info("Input from GPIO-%s w/ PULLOFF:  %s", \
                GPIO_IN, RPIO.input(GPIO_IN))
        RPIO.set_pullupdn(GPIO_IN, RPIO.PUD_UP)
        logging.info("Input from GPIO-%s w/ PULLUP:   %s", \
                GPIO_IN, RPIO.input(GPIO_IN))
        RPIO.set_pullupdn(GPIO_IN, RPIO.PUD_DOWN)
        logging.info("Input from GPIO-%s w/ PULLDOWN: %s", \
                GPIO_IN, RPIO.input(GPIO_IN))
        logging.info("--------------------------------------")
        logging.info(" ")
        RPIO.set_pullupdn(GPIO_IN, RPIO.PUD_OFF)

    def test4_output(self):
        with self.assertRaises(RPIO.InvalidChannelException):
            # 5 is not a valid gpio
            RPIO.setup(5, RPIO.OUT)
        with self.assertRaises(RPIO.InvalidChannelException):
            # 5 is not a valid gpio
            RPIO.setup(0, RPIO.OUT)
        with self.assertRaises(RPIO.InvalidChannelException):
            # 5 is not a valid gpio
            RPIO.setup(32, RPIO.OUT)

        logging.info("Setting up GPIO-%s as output...", GPIO_OUT)
        RPIO.setup(GPIO_OUT, RPIO.OUT)
        logging.info("Setting GPIO-%s output to 1...", GPIO_OUT)
        RPIO.output(GPIO_OUT, RPIO.HIGH)
        time.sleep(2)
        logging.info("Setting GPIO-%s output to 0...", GPIO_OUT)
        RPIO.output(GPIO_OUT, RPIO.LOW)

    def test5_board_pin_numbers(self):
        logging.info(" ")
        logging.info(" ")
        logging.info(" ")

        RPIO.setmode(RPIO.BCM)
        pins = RPIO.GPIO_LIST_R1 if RPIO.RPI_REVISION == 1 \
                else RPIO.GPIO_LIST_R2
        logging.info("testing bcm gpio numbering: %s", pins)
        for pin in pins:
            gpio_id = RPIO.channel_to_gpio(pin)
            logging.info("- BCM channel %s = gpio %s", pin, gpio_id)
        with self.assertRaises(RPIO.InvalidChannelException):
            gpio_id = RPIO.channel_to_gpio(32)
        with self.assertRaises(RPIO.InvalidChannelException):
            gpio_id = RPIO.channel_to_gpio(5)

        logging.info(" ")

        pins = RPIO.PIN_LIST
        RPIO.setmode(RPIO.BOARD)
        logging.info("testing board gpio numbering: %s", pins)
        for pin in pins:
            if pin >> 8 > 0:
                # py_gpio.c cannot deal with BOARD->BCM of P5 pins yet
                continue
            gpio_id = RPIO.channel_to_gpio(pin)
            logging.info("- BOARD channel %s = gpio %s", pin, gpio_id)
        with self.assertRaises(RPIO.InvalidChannelException):
            gpio_id = RPIO.channel_to_gpio(0)

        RPIO.setmode(RPIO.BCM)

    def test6_interrupts(self):
        def test_callback(*args):
            logging.info("- interrupt callback received: %s", (args))
            RPIO.stop_waiting_for_interrupts()

        logging.info(" ")
        logging.info(" ")
        logging.info(" ")
        logging.info("Testing interrupts on GPIO-%s", GPIO_IN)
        RPIO.add_interrupt_callback(GPIO_IN, test_callback, edge='rising', \
                pull_up_down=RPIO.PUD_DOWN)

        logging.info("- waiting for interrupts on GPIO-%s...", GPIO_IN)
        try:
            RPIO.wait_for_interrupts()
        except:
            pass

        logging.info("-")
        RPIO.cleanup()
        time.sleep(1)

        logging.info(" ")
        logging.info(" ")
        logging.info(" ")
        RPIO.add_interrupt_callback(GPIO_IN, test_callback, edge='falling', \
                pull_up_down=RPIO.PUD_UP)
        logging.info("- waiting for manual exit (CTRL+C) on GPIO-%s", GPIO_IN)
        try:
            RPIO.wait_for_interrupts()
        except:
            pass
        logging.info("- stopped waiting for interrupts on GPIO-%s", GPIO_IN)
        logging.info("-")
        RPIO.cleanup()
        RPIO.cleanup()


if __name__ == '__main__':
    unittest.main()
