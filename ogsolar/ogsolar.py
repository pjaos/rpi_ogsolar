#!/usr/bin/env python3.9

from optparse import OptionParser
from time import sleep
from getpass import getuser

from p3lib.uio import UIO
from p3lib.boot_manager import BootManager

from ogsolar.libs.app_config import AppConfig
from ogsolar.libs.startup_controller import StartupController
from ogsolar.libs.adc_interface import ADCInterface
from ogsolar.libs.adc_cal import ADCCalibration
from ogsolar.libs.gpio_control import GPIOControl
from ogsolar.libs.web_server import WebServer

def readVoltage(uio, options):
    """@brief Read the voltage."""
    adcInterface = ADCInterface(uio, options) 
    adcInterface.debugVoltage()

def readCurrent(uio, options):
    """@brief Read the current."""
    adcInterface = ADCInterface(uio, options) 
    adcInterface.debugCurrent()

def readHeatSinkTemp(uio, options):
    """@brief Read the temperature of the controllers heatsink."""
    adcInterface = ADCInterface(uio, options) 
    adcInterface.debugHeatSinkTempC()

def readCPUTemp(uio, options):
    """@brief Read the temperature of the RPi CPU."""
    adcInterface = ADCInterface(uio, options) 
    adcInterface.debugCPUTempC()

def stop():
    """@brief Wait around forever."""
    while True:
        sleep(10)

def setLoad1(uio, options):
    """@brief Set load 1 on/off
       @param uio A UIO instance.
       @param options argparse options instance."""
    gpioControl = GPIOControl(uio, options)   
    try:
        if options.l1 in [0,1]:
            gpioControl.setLoad1(options.l1)
            if options.l1:
                uio.info("Set load 1 ON")
            else:
                uio.info("Set load 1 OFF")
            stop()
        else:
            raise Exception("--l1 must be followed by 0 or 1.")
    finally:
        gpioControl.close()
    return
     
def setLoad2(uio, options):
    """@brief Set load 2 on/off
       @param uio A UIO instance.
       @param options argparse options instance."""
    gpioControl = GPIOControl(uio, options)   
    try:
        if options.l2 in [0,1]:
            gpioControl.setLoad2(options.l2)
            if options.l2:
                uio.info("Set load 2 ON")
            else:
                uio.info("Set load 2 OFF")
            stop()
        else:
            raise Exception("--l2 must be followed by 0 or 1.")
    finally:
        gpioControl.close()
    return

     
def setInverterRelay(uio, options):
    """@brief Set inverter relay output on/off
       @param uio A UIO instance.
       @param options argparse options instance."""
    gpioControl = GPIOControl(uio, options)   
    try:
        if options.invr in [0,1]:
            gpioControl.selectACMains(not options.invr)
            if options.invr:
                uio.info("Select inverter")
            else:
                uio.info("Select AC mains")
            stop()
        else:
            raise Exception("--invr must be followed by 0 or 1.")
    finally:
        gpioControl.close()
    return

def setSpareRelay(uio, options):
    """@brief Set spare relay output on/off
       @param uio A UIO instance.
       @param options argparse options instance."""
    gpioControl = GPIOControl(uio, options)   
    try:
        if options.sparer in [0,1]:
            gpioControl.selectACMains(not options.sparer)
            if options.sparer:
                uio.info("Set spare relay ON")
            else:
                uio.info("Set spare relay OFF")
            stop()
        else:
            raise Exception("--sparer must be followed by 0 or 1.")
    finally:
        gpioControl.close()
    return

def enableAutoStart(user):
    """@brief Enable this program to auto start when the computer on which it is installed starts.
       @param user The username which which you wish to execute on autostart."""
    bootManager = BootManager()
    if user:           
        bootManager.add(user=user, enableSyslog=True)
    else:
        raise Exception("--user not set.")

def disableAutoStart():
    """@brief Enable this program to auto start when the computer on which it is installed starts."""
    bootManager = BootManager()
    bootManager.remove()
        
def checkAutoStartStatus(uio):
    """@brief Check the status of a process previously set to auto start."""
    bootManager = BootManager()
    lines = bootManager.getStatus()
    if lines and len(lines) > 0:
        for line in lines:
            uio.info(line)
                
def main():

    options = None
    uio = UIO()

    opts=OptionParser(usage='An application to control an off grid solar installation. Specifically for use with an EPSolar Tracer MPPT controller connected to a battery (Lithium or Lead Acid). An inverter can be used to power devices when sufficient charge is available on the battery.')
    opts.add_option("--config",             help="Set the configuration parameters.", action="store_true", default=False)
    opts.add_option("--cal",                help="Calibrate the voltage and current measurements.", action="store_true", default=False)
    opts.add_option("--quiet",              help="Do not display messages on stdout.", action="store_true", default=False)
    opts.add_option("--inv_on",             help="On startup set the inverter on and select the inverter output. By default the inverter is off and mains AC is selected.", action="store_true", default=False)
    opts.add_option("--web_root",           help="The web root dir (default={}).".format(WebServer.GetWebRootFolder()), default=WebServer.GetWebRootFolder())
    opts.add_option("--max_mem_inc",        help="The maximum memory (RAM) increase of ogsolar controller software before rebooting the system (default = %d kB)." % (StartupController.MAX_MEM_INCREASE_KB) , type="int", default=StartupController.MAX_MEM_INCREASE_KB)
    opts.add_option("--sim_json",           help="Developer use only. Simulate tracer MPPT Ctrl hardware. A JSON file is needed as the argument. This is a file saved using menu option 2 when running the tracer command. This saves a JSON file with the state of all the tracer unit registers.", default=None)
    opts.add_option("--tracer_log",         help="Log file for EPSolar Tracer register values (default = none). If --sim_tracer is used then tracer register values are read from this file. If --sim_tracer is not used then register values read from the Tracer hardware are written (appended) to this file.", default=None)
    opts.add_option("--sim_ads1115",        help="Developer use only. Simulate the ADS1115 ADC on I2c bus hardware.", action="store_true", default=False)
    opts.add_option("--off",                help="Switch off inverter and spare relay.", action="store_true", default=False)
    opts.add_option("--debug",              help="Enable debugging.", action="store_true", default=False)
    opts.add_option("--no_reboot",          help="In the event of an error a reboot will occur to try and recover. If this option is used this does not occur.", action="store_true", default=False)
    opts.add_option("--enable_auto_start",  help="Auto start when this computer starts.", action="store_true", default=False)
    opts.add_option("--user",               help="The user name when the --enable_auto_start argument is used (default={})".format(getuser()), default=getuser())
    opts.add_option("--disable_auto_start", help="Disable auto starting when this computer starts.", action="store_true", default=False)
    opts.add_option("--check_auto_start",   help="Check the status of an auto started ogsolar instance.", action="store_true", default=False)
    
    #The following are debugging options used to test that the hardware was working when the HW was built.
    opts.add_option("--dv",                 help="Debug the voltage reading. Read and display the voltage every second.", action="store_true", default=False)
    opts.add_option("--dc",                 help="Debug the current reading. Read and display the current (Amps) every second.", action="store_true", default=False)
    opts.add_option("--dht",                help="Debug the heatsink temperature reading. Read and display the temperature every second.", action="store_true", default=False)
    opts.add_option("--dpt",                help="Debug the processor temperature reading. Read and display the temperature every second.", action="store_true", default=False)
    opts.add_option("--tgpio",              help="Toggle the GPIO lines for debugging purposes.", action="store_true", default=False)
    opts.add_option("--rsw",                help="Read the state of the switch for debugging purposes.", action="store_true", default=False)
    opts.add_option("--l1",                 help="Set load 1 on/off (1/0) for debugging purposes. This output should be connected to the inverter.", type=int, default=-1)
    opts.add_option("--l2",                 help="Set load 2 on/off (1/0) for debugging purposes.", type=int, default=-1)
    opts.add_option("--invr",               help="Set the inverter relay output on/off (1/0) for debugging purposes.", type=int, default=-1)
    opts.add_option("--sparer",             help="Set the spare relay output on/off (1/0) for debugging purposes.", type=int, default=-1)

    try:
        (options, args) = opts.parse_args()

        #Before starting any threads ensure we have a web root folder.
        WebServer.EnsureWebRootExists()
                    
        if options.debug:
            uio.enableDebug(options.debug)
        
        if options.quiet:
            uio.enableStdOut(False)
    
        if options.dv:
            readVoltage(uio, options)
            return

        if options.dc:
            readCurrent(uio, options)
            return

        if options.dht:
            readHeatSinkTemp(uio, options)
            return

        if options.dpt:
            readCPUTemp(uio, options)
            return

        if options.cal:
            adcCal = ADCCalibration(uio, options)
            adcCal.calibrate()
            return

        if options.tgpio:
            gpioControl = GPIOControl(uio, options)   
            try:
                gpioControl.toggleGPIO()
            finally:
                gpioControl.close()
            return
        
        if options.rsw:
            gpioControl = GPIOControl(uio, options)   
            try:
                gpioControl.readSW()
            finally:
                gpioControl.close()
            return

        if options.l1 != -1:
            setLoad1(uio, options)
            return

        if options.l2 != -1:
            setLoad2(uio, options)
            return
        
        if options.invr != -1:
            setInverterRelay(uio, options)
            return
        
        if options.sparer != -1:
            setSpareRelay(uio, options)
            return
        
        appConfig = AppConfig(uio)
        syslogServer = appConfig.getAttr(AppConfig.SYSLOG_SERVER)
        if syslogServer and len(syslogServer) > 0:
            uio.enableSyslog(True, host=syslogServer)

        uio.info("STARTUP: ogsolar")
        
        if options.config:
            appConfig.configure()

        elif options.enable_auto_start:
            enableAutoStart(options.user)

        elif options.disable_auto_start:
            disableAutoStart()
        
        elif options.check_auto_start:
            checkAutoStartStatus(uio)
            
        else:
            startupController = StartupController(uio, options, appConfig)
            startupController.run()
            

    #If the program throws a system exit exception
    except SystemExit:
        pass

    #Don't print error information if CTRL C pressed
    except KeyboardInterrupt:
        pass

    except Exception as ex:

        if options.debug:
            raise
        else:
            uio.error(str(ex))


if __name__== '__main__':
    main()
