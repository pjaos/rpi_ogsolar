# To Build ogsolar SD card for the Raspberry PI

# Create SD card

TODO This need to detail the way to get to this SD card image
```
sudo dd bs=4M status=progress conv=fsync if=with_tplink_usb_wifi_adaptor.bin of=/dev/sdd
```

# Update to the latest RPi (in my case buster) release

```
sudo apt update
sudo apt upgrade
```

# Install python3.9.7

```
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget curl
sudo apt install libssl-dev libffi-dev
cd /tmp
curl -O https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tar.xz
tar -xf Python-3.9.7.tar.xz
cd Python-3.9.7
./configure --enable-optimizations
sudo make altinstall
```

# Upgrade pip to the latest version

```
sudo python3.9 -m pip install --upgrade pip
```

# Add pipenv python package

```
sudo python3.9 -m pip install pipenv
```

# Check kernel version

```
pi@raspberrypi:~ $ uname -a
Linux raspberrypi 5.10.17-v7+ #1414 SMP Fri Apr 30 13:18:35 BST 2021 armv7l GNU/Linux
```

This will be used later when installing drivers.

# [Save RPi SD card](#save-rpi-sd-card)

# Setup USB Wifi

- Insert WiFi adaptor into USB port
The driver for the WiFi adaptor that you have must now be installed.
The following provides examples of how I installed the drivers for the
WiFi USB devices that I had. Yours may have different chip sets therefore
the commands may need to be altered accordingly.

## Install driver for TP link USB Wifi adaptor

```
cd /tmp
wget http://downloads.fars-robotics.net/wifi-drivers/8192eu-drivers/8192eu-5.10.60-v7-1449.tar.gz
tar xvf 8192eu-5.10.60-v7-1449.tar.gz
sudo ./install.sh
```

## Install driver for 802.11AC USB Wifi adaptor with SMA port

```
wget http://downloads.fars-robotics.net/wifi-drivers/8822bu-drivers/8822bu-5.10.60-v7-1449.tar.gz
tar xvf 8822bu-5.10.60-v7-1449.tar.gz
sudo ./install.sh
```

## Install driver for other MediaTech USB Wifi adaptor with SMA port

```
wget http://downloads.fars-robotics.net/wifi-drivers/8821cu-drivers/8821cu-5.10.60-v7-1449.tar.gz
tar xvf 8821cu-5.10.60-v7-1449.tar.gz
sudo ./install.sh
```

- Reboot RPi and login
- Check all Wifi interfaces work.
The command below shows wlan0 (RPi internal WiFi) and two USB WiFi adaptors running.
Only one USB WiFi adaptor is needed for the OGSolar project. The USB Wifi is used to
connect back to the house LAN. The internal RPi WiFi is used to provide a WiFi network
around the OGSolar RPi.

```
pi@raspberrypi:~ $ ip a show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc pfifo_fast state DOWN group default qlen 1000
    link/ether b8:27:eb:ec:6a:98 brd ff:ff:ff:ff:ff:ff
3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether b8:27:eb:b9:3f:cd brd ff:ff:ff:ff:ff:ff
    inet 192.168.0.224/24 brd 192.168.0.255 scope global dynamic noprefixroute wlan0
       valid_lft 86362sec preferred_lft 75562sec
    inet6 fe80::d146:62c2:479b:b3b/64 scope link
       valid_lft forever preferred_lft forever
4: wlan1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether e8:48:b8:c8:bd:37 brd ff:ff:ff:ff:ff:ff
    inet 192.168.0.128/24 brd 192.168.0.255 scope global dynamic noprefixroute wlan1
       valid_lft 86361sec preferred_lft 75561sec
    inet6 fe80::f5bb:8b2d:c176:30da/64 scope link
       valid_lft forever preferred_lft forever
5: wlan2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 1c:bf:ce:7f:54:a7 brd ff:ff:ff:ff:ff:ff
    inet 192.168.0.164/24 brd 192.168.0.255 scope global dynamic noprefixroute wlan2
       valid_lft 86367sec preferred_lft 75567sec
    inet6 fe80::8d3b:52e9:c228:c8f2/64 scope link
       valid_lft forever preferred_lft forever
```

# Add required packages for WiFi access point

```
sudo apt install -y hostapd isc-dhcp-server dnsmasq ne
```

- Ensure only one USB WiFi adaptor is connected to the RPi.

- Update network interface names (wint0 = the internal RPi Wifi interface, wusb1 = 80211AC USB Wifi)
The commands below will need to be updated with the MAC addresses of you internal and USB WiFi adaptors
as shown when you executed the 'ip a show' command'

```
sudo ne /etc/udev/rules.d/70-persistent-net.rules
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="b8:27:eb:b9:3f:cd", ATTR{type}=="1", KERNEL=="wlan*", NAME="wint0"
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="1c:bf:ce:7f:54:a7", ATTR{type}=="1", KERNEL=="wlan*", NAME="wusb1"
```

When the Rpi reboots it should come up with a wint0 and a wusb1 WiFi interface.


- Reboot the RPi and check network interfaces are renamed correctly

```
pi@raspberrypi:~ $ ip a show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc pfifo_fast state DOWN group default qlen 1000
    link/ether b8:27:eb:ec:6a:98 brd ff:ff:ff:ff:ff:ff
3: wint0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether b8:27:eb:b9:3f:cd brd ff:ff:ff:ff:ff:ff
    inet 192.168.0.224/24 brd 192.168.0.255 scope global dynamic noprefixroute wint0
       valid_lft 86383sec preferred_lft 75583sec
    inet6 fe80::d146:62c2:479b:b3b/64 scope link
       valid_lft forever preferred_lft forever
4: wusb1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 1c:bf:ce:7f:54:a7 brd ff:ff:ff:ff:ff:ff
    inet 192.168.0.164/24 brd 192.168.0.255 scope global dynamic noprefixroute wusb1
       valid_lft 86385sec preferred_lft 75585sec
    inet6 fe80::8d3b:52e9:c228:c8f2/64 scope link
       valid_lft forever preferred_lft forever
```

# [Save RPi SD card](#save-rpi-sd-card)

| :exclamation:  The following commands are executed as root user.   |
|-----------------------------------------|

- Add package to make iptables rules persistent.

```
DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent
```

- Setup wint0 to be used for ap WiFi interface and forward IP packets via wusb1

```
ne /etc/dhcpcd.conf
interface wint0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
ne /etc/sysctl.d/routed-ap.conf
net.ipv4.ip_forward=1
```

- Set firewall rule for RPi

```
iptables -t nat -A POSTROUTING -o wusb1 -j MASQUERADE
netfilter-persistent save
```

- Setup dnsmasq

```
mv /etc/dnsmasq.conf /root/dnsmasq.conf.orig
```

```
ne /etc/dnsmasq.conf
interface=wint0 # Listening interface
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
                # Pool of IP addresses served via DHCP
domain=wlan     # Local wireless DNS domain
address=/gw.wlan/192.168.4.1
                # Alias for this router

```

# Setup wireless AP
This uses the wint0 (internal RPi WiFi) interface on the RPi.

```
rfkill unblock wlan
```

```
cat > /etc/hostapd/hostapd.conf <<EOF
interface=wint0
driver=nl80211
ssid=<AP WIFI SSID>
country_code=GB
hw_mode=b
channel=6
auth_algs=3
wpa=2
ignore_broadcast_ssid=0
wpa_passphrase=<AP WIFI PASSWORD>
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF


systemctl unmask hostapd
systemctl enable hostapd
```

- If the USB WiFi adaptor used has an external antenna (SMA connector) then ensure this antenna is connected.

- Reboot and check that a device connected to the AP WiFi SSID. Your should be able to use a phone or tablet to do this.
  Ensure the device used has access to the internet.

# [Save RPi SD card](#save-rpi-sd-card)

# Ensure modules are installed to access the I2C bus and serial ports.

```
python3.9 -m pip install smbus
python3.9 -m pip install serial
apt install  i2c-tools
```

- Check that the I2C bus is enabled on the RPi
Run the raspi-config command and enable the I2C bus.

```
raspi-config Interfacing Options / P5 I2C / Enable Yes
```

- Without the OGsolar PCB connected to the RPi check that the I2C bus is working.

```
 i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

With the OGsolar PCB connected check that the ADC device can be seen on the I2C bus.

```
i2cdetect -y 1
    0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

- The platform is now ready to have the ogsolar application added.

# [Save RPi SD card](#save-rpi-sd-card)

# Install the ogsolar application.
Either checkout the git repository on the RPi and install as shown below

```
sudo python3.9 -m pip install pyflakes
cd into the git folder
sudo ./install.sh
```

# Change the RPi user from pi
For security purposes add another user and remove pi user as shown below.

- Add another user, in this case 'auser' and delete pi user

```
sudo adduser auser
Adding user `auser' ...
Adding new group `auser' (1001) ...
Adding new user `auser' (1001) with group `auser' ...
Creating home directory `/home/auser' ...
Copying files from `/etc/skel' ...
New password:
Retype new password:
passwd: password updated successfully
Changing the user information for auser
Enter the new value, or press ENTER for the default
	Full Name []:
	Room Number []:
	Work Phone []:
	Home Phone []:
	Other []:
Is the information correct? [Y/n] y
```

Add the new username to the list of sudoers (users that have root access).

```
sudo -s
root@raspberrypi:/home/pi#

sudo ne /etc/sudoers.d/010_auser-nopasswd
auser ALL=(ALL) NOPASSWD: ALL
```

### Allow non root access
Control GPIO pins as well as other functionality is required as a non
root user. The following command achieve this.

```
sudo adduser pi gpio
sudo adduser pi i2c
sudo adduser pi spi
sudo adduser pi dialout
```

### Check ssh access
Check that you can ssh to the RPi. ssh with username auser and check sudo -s
works.

```
ssh-copy-id auser@192.168.1.98
ssh auser@192.168.1.98
sudo -s
```
If the sudo command works you should be presented with the # prompt.
Now you know that you have access to the RPi using a different username
it is safe to remove the default pi user. This is done using the command
shown below.

```
sudo deluser --remove_home pi
```

# Using the OGSolar application.

The ogsolar application is a command line program. The command line help is shown below.

```
ogsolar -h
Usage: An application to control an off grid solar installation.
Specifically for use with an EPSolar Tracer MPPT controller connected to
a battery (Lithium or Lead Acid). An inverter can be used to power devices
when sufficient charge is available on the battery.

Options:
  -h, --help            show this help message and exit
  --config              Set the configuration parameters.
  --cal                 Calibrate the voltage and current measurements.
  --quiet               Do not display messages on stdout.
  --inv_on              On startup set the inverter on and select the inverter
                        output. By default the inverter is off and mains AC is
                        selected.
  --web_root=WEB_ROOT   The web root dir (default=/www).
  --max_mem_inc=MAX_MEM_INC
                        The maximum memory (RAM) increase of ogsolar
                        controller software before rebooting the system
                        (default = 10000 kB).
  --sim_json=SIM_JSON   Developer use only. Simulate tracer MPPT Ctrl
                        hardware. A JSON file is needed as the argument. This
                        is a file saved using menu option 2 when running the
                        tracer command. This saves a JSON file with the state
                        of all the tracer unit registers.
  --tracer_log=TRACER_LOG
                        Log file for EPSolar Tracer register values (default =
                        none). If --sim_tracer is used then tracer register
                        values are read from this file. If --sim_tracer is not
                        used then register values read from the Tracer
                        hardware are written (appended) to this file.
  --sim_ads1115         Developer use only. Simulate the ADS1115 ADC on I2c
                        bus hardware.
  --off                 Switch off inverter and spare relay.
  --debug               Enable debugging.
  --no_reboot           In the event of an error a reboot will occur to try
                        and recover. If this option is used this does not
                        occur.
  --enable_auto_start   Auto start when this computer starts.
  --user=USER           The user name when the --enable_auto_start argument is
                        used (default=auser)
  --disable_auto_start  Disable auto starting when this computer starts.
  --check_auto_start    Check the status of an auto started ogsolar instance.
  --dv                  Debug the voltage reading. Read and display the
                        voltage every second.
  --dc                  Debug the current reading. Read and display the
                        current (Amps) every second.
  --dht                 Debug the heatsink temperature reading. Read and
                        display the temperature every second.
  --dpt                 Debug the processor temperature reading. Read and
                        display the temperature every second.
  --tgpio               Toggle the GPIO lines for debugging purposes.
  --rsw                 Read the state of the switch for debugging purposes.
  --l1=L1               Set load 1 on/off (1/0) for debugging purposes. This
                        output should be connected to the inverter.
  --l2=L2               Set load 2 on/off (1/0) for debugging purposes.
  --invr=INVR           Set the inverter relay output on/off (1/0) for
                        debugging purposes.
  --sparer=SPARER       Set the spare relay output on/off (1/0) for debugging
                        purposes.
```

## Initial hardware configuration
Before the hardware can be used it must be calibrated. In order to do the the
RPi with the OGSolar PCB connected must be setup. In order to do this it should
be connected to a 16V DC power supply with a 6 ohm load resistor (the load
current must be at least one amp). Then run the following commands

```
ogsolar --cal
```

1 - You will be asked to measure the DC voltage. MEasure the voltage with a DMM
and enter the voltage measured.

2 - Press return and Load 1 will be turned on.

3 - Measure the DC current through the load and enter the value in amps. Press
return to complete the calibration.

This stores the .ogsolar_adc_cal.cfg (a test file) in the home dir that ensures
accurate current and voltage measurements.

## Configuration
The RPi must be configured when to turn loads 1 and 2 on and off. This can be
done using the --config argument. An example of this is shown below.

```
auser@@raspberrypi:~ $ ogsolar --config
INFO:  Loaded config from /home/auser/.ogsolar.cfg
INFO:  STARTUP: ogsolar
INFO:  ID  PARAMETER                  VALUE
INFO:  1   LOAD1_ON_VOLTAGE           15.95
INFO:  2   LOAD1_CUTOFF_VOLTAGE       14.8
INFO:  3   LOAD2_ON_VOLTAGE           15.95
INFO:  4   LOAD2_CUTOFF_VOLTAGE       14.4
INFO:  5   DELAY_BEFORE_ERROR_REBOOT  120
INFO:  6   SYSLOG_SERVER              192.168.1.102
INFO:  7   TRACER_MPPT_SERIAL_PORT    /dev/ttyUSB0
INFO:  8   TRACER_MPPT_POLL_SECONDS   5
INFO:  9   ALLOW_BATTERY_LOAD_ON      y
INPUT: Enter 'E' to edit a parameter, 'S' to save and quit or 'Q' to quit:
```

The values shown above were configured for a Lithium ION battery with 4 serial
cells and place the focus on battery longevity rather than battery charge
capacity. If a lead acid battery is connected in the system then the
voltages will be lower. It is the users responsibility to set the values
appropriate for the battery used in the system. The syslog server
configuration is only required if you have a syslog server on your
network to log data for debugging purposes.

## Checking that the application is running.
With the RPi (with OGSolar PCB connected) connected to a USB RS485 adaptor. An
isolated RS485 adaptor should be used due to the positive ground of the EPSolar
Tracer.

You should enter 'ogsolar' on the command line and check that the system and
check that the system runs correctly as shown below.

```
ogsolar
INFO:  Loaded config from /home/auser/.ogsolar.cfg
INFO:  STARTUP: ogsolar
INFO:  Listening on UDP port 2934
INFO:  Starting web server.
INFO:  Turn spare relay OFF
INFO:  select AC source from Mains AC
INFO:  Set inverter output OFF.
INFO:  Set inverter output OFF.
INFO:  Loaded config from /home/auser/.ogsolar_adc_cal.cfg
INFO:  Set inverter off initial state.
INFO:  Set inverter output OFF.
INFO:  Turned load 1 OFF
INFO:  select AC source from Mains AC
INFO:  ------------------> Selected AC from mains supply.
INFO:  Set inverter output ON.
INFO:  Turned load 2 ON
INFO:  Heat sink: 19.3 °C
INFO:  CPU:       37.1 °C
INFO:  Load AMPS: 0.364, Load WATTS 5.616
INFO:  Battery charge state = Not Charging
INFO:  Load 1 OFF:  Battery volts: 15.230. Waiting for battery voltage to reach 15.950 volts.
INFO:  Load 2 ON:  Battery volts: 15.230. Waiting for battery voltage to drop to 14.400 volts.
INFO:  STARTUP: 9 threads running
INFO:  9 threads running (min=8).
INFO:  Memory in use = 18408 kB, increase since startup = 0 kB (max = 10000 kB).
INFO:  9 threads running (min=8).
INFO:  Memory in use = 18580 kB, increase since startup = 172 kB (max = 10000 kB).
INFO:  Heat sink: 19.3 °C
INFO:  CPU:       37.1 °C
INFO:  Load AMPS: 0.827, Load WATTS 12.729
INFO:  Battery charge state = Not Charging
INFO:  Load 1 OFF:  Battery volts: 15.210. Waiting for battery voltage to reach 15.950 volts.
INFO:  Load 2 ON:  Battery volts: 15.210. Waiting for battery voltage to drop to 14.400 volts.
INFO:  Seconds since last AYT reception: 5
INFO:  Listening on UDP port 2934
INFO:  9 threads running (min=8).
INFO:  Memory in use = 18760 kB, increase since startup = 352 kB (max = 10000 kB).
INFO:  ipAddress=192.168.1.98
INFO:  Turned LED ON
INFO:  Heat sink: 19.3 °C
INFO:  CPU:       37.0 °C
INFO:  Load AMPS: 0.824, Load WATTS 12.679
INFO:  Battery charge state = Not Charging
INFO:  Load 1 OFF:  Battery volts: 15.210. Waiting for battery voltage to reach 15.950 volts.
INFO:  Load 2 ON:  Battery volts: 15.210. Waiting for battery voltage to drop to 14.400 volts.
INFO:  9 threads running (min=8).
INFO:  Memory in use = 18760 kB, increase since startup = 352 kB (max = 10000 kB).
INFO:  Seconds since last AYT reception: 5
INFO:  Listening on UDP port 2934
INFO:  ipAddress=192.168.1.98
INFO:  9 threads running (min=8).
INFO:  Memory in use = 18760 kB, increase since startup = 352 kB (max = 10000 kB).
INFO:  Heat sink: 19.3 °C
INFO:  CPU:       37.0 °C
INFO:  Load AMPS: 0.825, Load WATTS 12.690
INFO:  Battery charge state = Not Charging
INFO:  Load 1 OFF:  Battery volts: 15.210. Waiting for battery voltage to reach 15.950 volts.
INFO:  Load 2 ON:  Battery volts: 15.210. Waiting for battery voltage to drop to 14.400 volts.
INFO:  9 threads running (min=8).
INFO:  Memory in use = 18760 kB, increase since startup = 352 kB (max = 10000 kB).
INFO:  ipAddress=192.168.1.98
INFO:  Heat sink: 19.3 °C
INFO:  CPU:       37.0 °C
INFO:  Load AMPS: 0.828, Load WATTS 12.741
INFO:  Battery charge state = Not Charging
INFO:  Load 1 OFF:  Battery volts: 15.210. Waiting for battery voltage to reach 15.950 volts.
INFO:  Load 2 ON:  Battery volts: 15.210. Waiting for battery voltage to drop to 14.400 volts.
INFO:  9 threads running (min=8).
INFO:  Memory in use = 18760 kB, increase since startup = 352 kB (max = 10000 kB).
INFO:  ipAddress=192.168.1.98
INFO:  9 threads running (min=8).
INFO:  Memory in use = 18760 kB, increase since startup = 352 kB (max = 10000 kB).
INFO:  Seconds since last AYT reception: 5
INFO:  Listening on UDP port 2934
INFO:  Heat sink: 19.3 °C
INFO:  CPU:       37.0 °C
INFO:  Load AMPS: 0.828, Load WATTS 12.742
INFO:  Battery charge state = Not Charging
INFO:  Load 1 OFF:  Battery volts: 15.210. Waiting for battery voltage to reach 15.950 volts.
INFO:  Load 2 ON:  Battery volts: 15.210. Waiting for battery voltage to drop to 14.400 volts.
```

## Configuring auto start.
Now that the ystem is configured and ready to run the ogsolar application needs
to startup when the RPi powers up. To do this enter the following command.

```
sudo ogsolar --user auser --enable_auto_start
INFO:  Loaded config from /root/.ogsolar.cfg
INFO:  STARTUP: ogsolar
```

Once started check that the ogsolar service has been started as shown below.

```
sudo ogsolar --check_auto_start
INFO:  Loaded config from /root/.ogsolar.cfg
INFO:  STARTUP: ogsolar
INFO:  ● ogsolar.service
INFO:     Loaded: loaded (/etc/systemd/system/ogsolar.service; enabled; vendor preset: enabled)
INFO:     Active: active (running) since Fri 2021-10-15 19:54:33 BST; 11s ago
INFO:   Main PID: 24554 (ogsolar)
INFO:      Tasks: 10 (limit: 2059)
INFO:     CGroup: /system.slice/ogsolar.service
INFO:             ├─24554 /bin/sh /usr/local/bin/ogsolar
INFO:             └─24555 python3.9 -u -m ogsolar.ogsolar
```

To cancel the auto start the following command may be used.

```
sudo ogsolar --disable_auto_start
```

| :exclamation:  Note that the The Rpi will reboot periodically if un configured or the EPSolar Tracer MPPT Charger is not connected via a USB RS485 adaptor.   |
|-----------------------------------------|

## Disable syslog.
If syslog is left runniong on the Raspberry PI then it will shortent the life of the SD card due to the data written to it during normal operation. 
OGSsolar also updates syslog data. Therefore it is useful to disable the syslog server on the Raspberry PI. This can be done using the following commands.

```
sudo systemctl stop syslog
sudo systemctl disable syslog
```

# [Save RPi SD card](#save-rpi-sd-card)

The RPi is now running the OGSolar system.


------------------------------------------------------------

# Save RPi SD card

- Shutdown the Raspberry PI

```
sudo halt
```

- Power down RPi, remove SD card and install in USB3 SD card reader connected to Ubuntu PC.

- Use gparted (install if not present) to reduce the rootfs size leaving 200 MB of
  free disk space.

- Save sd card image saving ~ 500MB more than the used disk space.
The command below sets the count to 900. 900*4M = 3.6 GB which in this case was 500 MB
more than the disk space used. When you run the command set the count value for the
disk space used on your SD card.

E.G

```
sudo dd bs=4M status=progress count=900 conv=fsync if=/dev/sde of=P3BPlus_README1.bin
```

- Restore the state of the sd card from the above image to check recovery works.

```
sudo dd bs=4M status=progress conv=fsync if=P3BPlus_README1.bin of=/dev/sde
```

- Use gparted to increase the rootfs partition size to use all the available disk space.

- Reinstall SD card in RPi, boot and login

--------------------------------------------
# Alternative internet connection.
The setup described above allows the USB WiFi connection to be used for internet
access (connection to the house LAN). If you wish to connect to the house LAN
via the physical Ethernet port on the RPi rather than from wusb1 (WiFi interface)
the following commands will change the configuration.

```
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
netfilter-persistent save
```

You will then need to connect an Ethernet cable from your router to the RPi.
The router must use DHCP to serve the RPi with an IP address.
