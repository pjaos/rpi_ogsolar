from time import sleep
try:

    import RPi.GPIO as gpio
    
except ImportError:
    class gpio(object):
        """@brief Dummy class to allow testing on non Raspberry PI platform."""    
        BCM = 1
        OUT = 1
        LOW = 0
        HIGH = 1
        @staticmethod
        def setmode(mode):
            print("gpio:setmode({})".format(mode))
        
        @staticmethod
        def setup(pin, mode):
            print("gpio:setup({},{})".format(pin, mode))
        
        @staticmethod
        def output(pin, state):
            print("gpio:output({},{})".format(pin, state))
    
class GPIOControl(object):

    MAINS_AC_RELAY_PIN         = 19
    SPARE_RELAY_PIN            = 26
    LED_PIN                    = 13
    LOAD_1_PIN                 = 21
    LOAD_2_PIN                 = 20
    SW_PIN                     = 6
    
    DC_POWER_ON                = 1
    DC_POWER_OFF               = 0

    AC_SOURCE_MAINS            = 0
    AC_SOURCE_INVERTER         = 1

    
    def __init__(self, uio, options):
        """@brief Constructor
           @param uio A UserIO instance
           @param options command line options object."""
        self._uio                   = uio
        self._options               = options
        
        gpio.setmode(gpio.BCM)
        gpio.setup(GPIOControl.LED_PIN, gpio.OUT)
        gpio.setup(GPIOControl.SPARE_RELAY_PIN, gpio.OUT)
        gpio.setup(GPIOControl.MAINS_AC_RELAY_PIN, gpio.OUT)
        gpio.setup(GPIOControl.LOAD_1_PIN, gpio.OUT)
        gpio.setup(GPIOControl.LOAD_2_PIN, gpio.OUT)

        gpio.setup(GPIOControl.SW_PIN, gpio.IN)
        
        self.setLoadOff()
        
        self._ledState = False
        
    def close(self):
        """@brief Called when program shuts down."""
        try:
            gpio.cleanup()
        except:
            pass
        
    def spare(self, on):
        """@brief Turn on/off the spare relay output.
           @param on True = on."""
        if on:
            gpio.output(GPIOControl.SPARE_RELAY_PIN, gpio.HIGH)
            pwrStr = "ON"
        else:
            gpio.output(GPIOControl.SPARE_RELAY_PIN, gpio.LOW)
            pwrStr = "OFF"

        self._uio.info("Turn spare relay %s" % (pwrStr) )

    def selectACMains(self, on):
        """@brief Turn on/off the AC power relay. When off the mains power comes from the mains AC.
                  When on the AC power is supplied from the inverter.
           @param on True = select the AC power from mains supply.
                     False = select the AC power from the inverter (load 1 must be on)."""
        if on:
            gpio.output(GPIOControl.MAINS_AC_RELAY_PIN, gpio.LOW)
            pwrStr = "Mains AC"
        else:
            gpio.output(GPIOControl.MAINS_AC_RELAY_PIN, gpio.HIGH)
            pwrStr = "Inverter OP"

        self._uio.info("select AC source from %s" % (pwrStr) )

    def setLoadOff(self):
        """@brief Set the load off so that it's not powered from the mains and
                  the dc power is off."""
        self.spare(False)
        self.selectACMains(True)
        self.setLoad1(False)
        self.setLoad2(False)

    def setLed(self, on):
        """@brief Turn on/off the LED
           @param on True = on."""
        if self._ledState != on:

            if on:
                gpio.output(GPIOControl.LED_PIN, gpio.HIGH)
                stateStr = "ON"
            else:
                gpio.output(GPIOControl.LED_PIN, gpio.LOW)
                stateStr = "OFF"

            self._uio.info("Turned LED %s" % (stateStr))
            self._ledState = on
            
    def setLoad1(self, on):
        """@brief Set Load 1 output on/off. This output is connected to an inverter.
           @param on If True turn power on."""

        if on:
            gpio.output(GPIOControl.LOAD_1_PIN, gpio.HIGH)
            pwrStr = "ON"
        else:
            gpio.output(GPIOControl.LOAD_1_PIN, gpio.LOW)
            pwrStr = "OFF"

        self._uio.info("Set inverter output {}.".format(pwrStr) )
        
    def setLoad2(self, on):
        """@brief Set Load 2 output on/off. This output is connected to the 12V
                  power supplied to the house.
           @param on If True turn power on."""

        if on:
            gpio.output(GPIOControl.LOAD_2_PIN, gpio.HIGH)
            pwrStr = "ON"
        else:
            gpio.output(GPIOControl.LOAD_2_PIN, gpio.LOW)
            pwrStr = "OFF"

        self._uio.info("Set inverter output {}.".format(pwrStr) )
        
    def toggleGPIO(self):
        """@brief Toggle all the following GPIO lines for debugging purposes.
                  - LED 
                  - LOAD 1
                  - Load 2
                  - AC mains
                  - Spare"""
        on = True
        while True:
                            
            self.setLed(on)
            self.setLoad1(on)
            self.setLoad2(on)
            self.selectACMains(on)
            self.spare(on)
            if on:
                self._uio.info("Set GPIO's HIGH")
                on = False
            else:
                self._uio.info("Set GPIO's LOW")
                on = True
                
            sleep(1)
            
    def readSW(self):
        """@brief Read the GPIO pin connected to the SW."""
        
        currentPinState = gpio.input(GPIOControl.SW_PIN)
        if currentPinState:
            self._uio.info("SW not pressed")            
        else:
            self._uio.info("SW pressed")
            
        while True:
            
            newPinState = gpio.input(GPIOControl.SW_PIN)
            if newPinState != currentPinState:
                currentPinState = newPinState
                if currentPinState:
                    self._uio.info("SW not pressed")            
                else:
                    self._uio.info("SW pressed")
            
            sleep(0.1)
                
            
