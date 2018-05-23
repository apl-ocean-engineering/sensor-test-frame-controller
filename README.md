# sensor-test-frame-controller

Currently using Beaglebone Debian image:

    $ cat /etc/dogtag
    BeagleBoard.org Debian Image 2018-01-28

Which contains

    $ python --version
    Python 2.7.13

    $ python3 --version
    Python 3.5.3


## Installing `pip` for python3

This Debian image does not include pip for python3 by default.  To install it:

    sudo apt-get update
    sudo apt-get install -y python3-pip

## Installing the Adafruit BBIO library


On Python 2:

    pip install Adafruit_BBIO

On Python 3:

    sudo apt-get install -y python3-smbus
    pip3 install Adafruit_BBIO

  Test that it worked (replace `python` with `python3` to test Python 3):

     $ python -c "import Adafruit_BBIO.GPIO as GPIO; print(GPIO)"
     <module 'Adafruit_BBIO.GPIO' from '/home/debian/.cache/Python-Eggs/Adafruit_BBIO-1.0.10-py2.7-linux-armv7l.egg-tmp/Adafruit_BBIO/GPIO.so'>

Hooray [this](https://learn.adafruit.com/blinking-an-led-with-beaglebone-black/the-python-console) works!

![](images/led.gif)


## Installing this package

    pip install --user -e .

To automatically install the development dependencies

    pip install --user -e .[dev]

If you change the gRPC prototype defined in `frame_controller/frame_controller.proto`, you must install the development dependencies about, then run `make proto` to rebuild the protobuf definitions.


## Running the package NOT on a Beaglebone Black

`apps/frame_server` is the entrypoint for the frame server.

In one window, run:

    python apps/frame_server --fake-hardware

In another window:

    python apps/frame_client
    
    
-----

# Hardware Config

In the current configuration,

IMU 1 RX; UART1_RXD; P9.26
IMU 1 TX; UART1_TXD; P9.24
IMU 2 RX; UART4_RXD; P9.11
IMU 2 TX; UART4_TXD; P9.13

Using these serial ports requires configuring the pins on the BBB.  This can be done manually with the `config-pin` command.   To query the current pin status:

    $ config-pin  -q p9.11
    P9_11 Mode: default Direction: in Value: 0

In this case P9.11 is current set as a GPIO, not as a UART.   To set as a UART (and P9.13 as well):

    $ config-pin p9.11 uart
    $ config-pin p9.13 uart
    
 Querying again:
 
     $ config-pin  -q p9.11
    P9_11 Mode: uart
    
To make this happen automatically, added it to `/etc/rc.local`


This is the current PWM configuration:


    M1_PWM_PIN = "P9_14"
    M1_DIRECTION_PIN = "P9_12"

    M2_PWM_PIN = "P9_16"
    M2_DIRECTION_PIN = "P9_15"

    M3_PWM_PIN = "P9_21"
    M3_DIRECTION_PIN = "P9_23"

    M4_PWM_PIN = "P9_22"
    M4_DIRECTION_PIN = "P9_41"
