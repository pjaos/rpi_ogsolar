#!/usr/bin/env python

from   optparse import OptionParser
from   subprocess import call
from   time import sleep
import sys

from   p3lib.uio import UIO
from   p3lib.pconfig import ConfigManager

class WiFiWatchDog(object):
    """@brief Responsible for maintaining WiFi connectivity."""

    WIFI_SSID                           = "WiFi SSID"
    WIFI_PASSWORD                       = "WiFi password"
    PINGABLE_IP_ADDRESS                 = "Pingable address"
    PING_CHECK_INTERVAL_SECS            = "Ping check interval (seconds)"
    LEVEL_1_TIMEOUT                     = "Level 1 WiFi setup interval (seconds)"
    LEVEL_2_TIMEOUT                     = "LEvel 2 reboot interval (seconds)"
    SYSLOG_SERVER                       = "Syslog server address"

    CONFIG_FILE                         = "wifi_watchdog.cfg"
    DEFAULT_CONFIG = {
        WIFI_SSID:                  "",
        WIFI_PASSWORD:              "",
        PINGABLE_IP_ADDRESS:        "",
        PING_CHECK_INTERVAL_SECS:   30,
        LEVEL_1_TIMEOUT:            300,
        LEVEL_2_TIMEOUT:            900,
        SYSLOG_SERVER:               ""
    }
    
    PING_CMD                            = "/bin/ping"
    SETUP_WIFI_CMD                      = "/sbin/setwifi"
    REBOOT                              = "/sbin/reboot"

    def __init__(self, uio):
        """@brief Constructor."""
        self._uio     = uio

        self._configManager = ConfigManager(self._uio, WiFiWatchDog.CONFIG_FILE, WiFiWatchDog.DEFAULT_CONFIG)
        self._configManager.load()

        self._uio.setSyslogServer( self._configManager.getAttr(WiFiWatchDog.SYSLOG_SERVER) )

    def configure(self):
        """@brief Configure the params."""

        self._configManager.inputStr(   WiFiWatchDog.WIFI_SSID, "Enter WiFi network/SSID", False)
        self._configManager.inputStr(   WiFiWatchDog.WIFI_PASSWORD, "Enter the WiFi network/SSID password", False)
        self._configManager.inputStr(   WiFiWatchDog.PINGABLE_IP_ADDRESS, "Enter the 'pingable' address that will be used to check if the WiFi is working", False)
        self._configManager.inputFloat( WiFiWatchDog.PING_CHECK_INTERVAL_SECS, "Enter the interval (in seconds) to check that the 'pingable' address is reachable." , minValue=0.5, maxValue=20000)
        self._configManager.inputDecInt( WiFiWatchDog.LEVEL_1_TIMEOUT, "Enter the level 1 (restart WiFi interface) ping failure count" , minValue=1, maxValue=10000)
        self._configManager.inputDecInt( WiFiWatchDog.LEVEL_2_TIMEOUT, "Enter the level 2 (reboot Linux) ping failure count" , minValue=2, maxValue=20000)

        self._configManager.inputStr(   WiFiWatchDog.SYSLOG_SERVER, "Enter the syslog server address if required", True)
        
        self._configManager.store()
        
    def _isPingable(self):
        """@brief Check if we can ping the pingable address."""
        #Reading config attr here means that they can be reconfigured on the fly
        pingDest = self._configManager.getAttr(WiFiWatchDog.PINGABLE_IP_ADDRESS)
        pingIntervalSecs = int( self._configManager.getAttr(WiFiWatchDog.PING_CHECK_INTERVAL_SECS) )
        cmd = "%s -c 1 -W %d %s > /dev/null 2>&1" % ( WiFiWatchDog.PING_CMD, pingIntervalSecs, pingDest)
        self._uio.info("Checking %s is pingable." % (pingDest) )
        returnCode = call(cmd, shell=True)
        
        if returnCode == 0:
            self._uio.info("%s is pingable." % (pingDest) )
            return True
        
        self._uio.error("Unable to ping %s" % (pingDest) )
        return False
        
    def _reConfigWiFi(self):
        """@brief Reconfigure the WiFi in an attempt to get it working."""
        ssid = self._configManager.getAttr(WiFiWatchDog.WIFI_SSID)
        password = self._configManager.getAttr(WiFiWatchDog.WIFI_PASSWORD)
        cmd = "%s %s %s" % ( WiFiWatchDog.SETUP_WIFI_CMD, ssid, password)
        call(cmd, shell=True)

    def _reboot(self):
        """@brief Reboot command."""
        call(WiFiWatchDog.REBOOT, shell=True)
    
    def start(self):
        """@brief Called to start the watchdog running."""
        
        #If not configured then configure
        if len(self._configManager.getAttr(WiFiWatchDog.WIFI_SSID)) == 0 or\
           len(self._configManager.getAttr(WiFiWatchDog.WIFI_PASSWORD)) == 0 or\
           len(self._configManager.getAttr(WiFiWatchDog.PINGABLE_IP_ADDRESS)) == 0:
            self.configure()

        if not self._isPingable():
            self._uio.info("Ping failed on startup.")
                        
        pingFailCount = 0
        while True:
            
            if self._isPingable():
                pingFailCount = 0
            else:
                pingFailCount = pingFailCount + 1
             
            #Reading config attr here means that they can be reconfigured on the fly   
            level1FailCount = int( self._configManager.getAttr(WiFiWatchDog.LEVEL_1_TIMEOUT) )
            level2FailCount = int( self._configManager.getAttr(WiFiWatchDog.LEVEL_2_TIMEOUT) )
            pingIntervalSecs = float( self._configManager.getAttr(WiFiWatchDog.PING_CHECK_INTERVAL_SECS) )
            self._uio.setSyslogServer( self._configManager.getAttr(WiFiWatchDog.SYSLOG_SERVER) )
            
            if pingFailCount > 0:
                 self._uio.info("Ping fail count = %d (level 1=%d, level 2 = %d)" % (pingFailCount, level1FailCount, level2FailCount) )

            if pingFailCount >= level2FailCount:
                self._reboot()
                
            if pingFailCount >= level1FailCount:
                self._reConfigWiFi()
                
            self._uio.info("Wait for %.1f seconds" % (pingIntervalSecs) )
            sleep(pingIntervalSecs)
                
            
            
        
if __name__== '__main__':

    options = None
    uio = UIO()

    opts=OptionParser(usage='A watchdog for WiFi connectivity. This script attem,pts to ensure we maintain WiFi connectivity. If WiFi connectivity is lost we first (level 1) attempt (at intervals) to setup the WiFi to regain connectivity. If this fails and the second level is reached then a reboot is performed in an attempt to regain network connectivity.')
    opts.add_option("-c",           help="Configure the options.", action="store_true", default=False)
    opts.add_option("--quiet",      help="Do not display messages on stdout.", action="store_true", default=False)
    opts.add_option("--debug",              help="Enable debugging.", action="store_true", default=False)

    try:
        (options, args) = opts.parse_args()
        
        wiFiWatchDog = WiFiWatchDog(uio)

        if options.quiet:
            uio.enableStdOut(False)
            
        if options.c:
            wiFiWatchDog.configure()
            
        else:
            wiFiWatchDog.start()            

    #If the program throws a system exit exception
    except SystemExit:
        pass

    #Don't print error information if CTRL C pressed
    except KeyboardInterrupt:
        pass

    except:
        if options and options.debug:
            raise
        else:
            uio.error(sys.exc_value[0])

