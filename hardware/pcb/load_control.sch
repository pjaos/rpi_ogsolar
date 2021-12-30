EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 2 2
Title "OGSOLAR RPi Interface"
Date ""
Rev "1.4"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Analog_ADC:ADS1115IDGS U3
U 1 1 60EDA87E
P 3350 3550
F 0 "U3" H 3350 4231 50  0000 C CNN
F 1 "ADS1115IDGS" H 3350 4140 50  0000 C CNN
F 2 "Package_SO:VSSOP-10_3x3mm_P0.5mm" H 3350 3050 50  0001 C CNN
F 3 "http://www.ti.com/lit/ds/symlink/ads1113.pdf" H 3300 2650 50  0001 C CNN
	1    3350 3550
	-1   0    0    -1  
$EndComp
NoConn ~ 2950 3350
Wire Wire Line
	3350 4650 3350 3950
Wire Wire Line
	2950 3750 2900 3750
Wire Wire Line
	2900 3750 2900 4650
Connection ~ 2900 4650
Wire Wire Line
	2900 4650 3350 4650
Wire Wire Line
	2700 3050 2600 3050
Wire Wire Line
	2700 3050 3350 3050
Connection ~ 2700 3050
Wire Wire Line
	3750 3550 3950 3550
Wire Wire Line
	3950 3550 3950 4650
Wire Wire Line
	3950 4650 3650 4650
Connection ~ 3350 4650
$Comp
L Connector:Conn_01x01_Male J8
U 1 1 60F9C91B
P 9500 4750
F 0 "J8" H 9472 4682 50  0000 R CNN
F 1 "To Shunt Resistor" H 9472 4773 50  0000 R CNN
F 2 "MountingHole:MountingHole_2.5mm_Pad_Via" H 9500 4750 50  0001 C CNN
F 3 "~" H 9500 4750 50  0001 C CNN
	1    9500 4750
	-1   0    0    1   
$EndComp
$Comp
L Device:Q_NMOS_DGS Q8
U 1 1 60FA2322
P 8100 4400
F 0 "Q8" H 8305 4446 50  0000 L CNN
F 1 "FQA70N10" H 8305 4355 50  0000 L CNN
F 2 "PJA_From_Eagle:TO-3PN__Vertical" H 8300 4500 50  0001 C CNN
F 3 "~" H 8100 4400 50  0001 C CNN
	1    8100 4400
	1    0    0    -1  
$EndComp
Wire Wire Line
	8200 4750 8200 4600
Wire Wire Line
	3750 3450 4450 3450
Wire Wire Line
	4950 3450 4950 4750
$Comp
L Connector:Conn_01x01_Male J7
U 1 1 60FB4EFD
P 9500 4350
F 0 "J7" H 9608 4531 50  0000 C CNN
F 1 "Load 1 (Inverter)" H 9608 4440 50  0000 C CNN
F 2 "MountingHole:MountingHole_2.5mm_Pad_Via" H 9500 4350 50  0001 C CNN
F 3 "~" H 9500 4350 50  0001 C CNN
	1    9500 4350
	-1   0    0    1   
$EndComp
Wire Wire Line
	8700 4350 8700 4200
Wire Wire Line
	8700 4200 8200 4200
$Comp
L Device:Q_NMOS_DGS Q7
U 1 1 60FE90AA
P 8100 3550
F 0 "Q7" H 8305 3596 50  0000 L CNN
F 1 "FQA70N10" H 8305 3505 50  0000 L CNN
F 2 "PJA_From_Eagle:TO-3PN__Vertical" H 8300 3650 50  0001 C CNN
F 3 "~" H 8100 3550 50  0001 C CNN
	1    8100 3550
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x01_Male J6
U 1 1 60FEA837
P 9500 3300
F 0 "J6" H 9608 3481 50  0000 C CNN
F 1 "Load 2 (Spare)" H 9608 3390 50  0000 C CNN
F 2 "MountingHole:MountingHole_2.5mm_Pad_Via" H 9500 3300 50  0001 C CNN
F 3 "~" H 9500 3300 50  0001 C CNN
	1    9500 3300
	-1   0    0    1   
$EndComp
Wire Wire Line
	8200 3300 8200 3350
Wire Wire Line
	8200 3750 8900 3750
Wire Wire Line
	8900 3750 8900 4750
Connection ~ 8900 4750
Wire Wire Line
	7900 3550 7500 3550
Wire Wire Line
	7900 4400 7800 4400
$Comp
L Device:R R8
U 1 1 610375F0
P 5850 3150
F 0 "R8" H 5920 3196 50  0000 L CNN
F 1 "100K" H 5920 3105 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 5780 3150 50  0001 C CNN
F 3 "~" H 5850 3150 50  0001 C CNN
	1    5850 3150
	0    1    1    0   
$EndComp
Wire Wire Line
	6500 3950 5150 3950
Wire Wire Line
	7450 3950 7350 3950
$Comp
L Device:R R13
U 1 1 61089ABC
P 7350 4100
F 0 "R13" H 7420 4146 50  0000 L CNN
F 1 "10K" H 7420 4055 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 7280 4100 50  0001 C CNN
F 3 "~" H 7350 4100 50  0001 C CNN
	1    7350 4100
	-1   0    0    1   
$EndComp
Connection ~ 7350 3950
Wire Wire Line
	7350 3950 6800 3950
$Comp
L Device:R R9
U 1 1 6108C3F6
P 6100 3300
F 0 "R9" H 5950 3350 50  0000 L CNN
F 1 "10K" H 5900 3250 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 6030 3300 50  0001 C CNN
F 3 "~" H 6100 3300 50  0001 C CNN
	1    6100 3300
	-1   0    0    1   
$EndComp
Wire Wire Line
	6100 3150 6000 3150
Connection ~ 3950 4650
Wire Wire Line
	5150 3000 5150 3150
Wire Wire Line
	6100 3850 6100 4650
Connection ~ 6100 4650
Text GLabel 5650 3650 0    60   Input ~ 0
L2
Wire Wire Line
	5700 3150 5150 3150
Connection ~ 5150 3150
Wire Wire Line
	5150 3150 5150 3950
Wire Wire Line
	7200 3200 6400 3200
Wire Wire Line
	6400 3200 6400 3150
Wire Wire Line
	6400 3150 6100 3150
Connection ~ 6100 3150
Wire Wire Line
	8200 3300 8450 3300
Wire Wire Line
	8700 4350 9300 4350
Wire Wire Line
	8900 4750 9200 4750
$Comp
L Device:R R14
U 1 1 6118DEE8
P 7400 4750
F 0 "R14" H 7470 4796 50  0000 L CNN
F 1 "4k7" H 7470 4705 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 7330 4750 50  0001 C CNN
F 3 "~" H 7400 4750 50  0001 C CNN
	1    7400 4750
	0    1    1    0   
$EndComp
Wire Wire Line
	8200 4750 7800 4750
Connection ~ 8200 4750
Wire Wire Line
	7250 4750 4950 4750
$Comp
L Device:D_Zener D8
U 1 1 611BAFEF
P 4750 4100
F 0 "D8" V 4704 4179 50  0000 L CNN
F 1 "3V9" V 4795 4179 50  0000 L CNN
F 2 "Diode_SMD:D_MicroMELF_Handsoldering" H 4750 4100 50  0001 C CNN
F 3 "~" H 4750 4100 50  0001 C CNN
	1    4750 4100
	0    1    1    0   
$EndComp
$Comp
L Device:C C8
U 1 1 611BBF3B
P 4450 4100
F 0 "C8" H 4500 4300 50  0000 L CNN
F 1 "0.1uf" H 4500 4200 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder" H 4488 3950 50  0001 C CNN
F 3 "~" H 4450 4100 50  0001 C CNN
	1    4450 4100
	1    0    0    -1  
$EndComp
Wire Wire Line
	4750 4250 4750 4650
Connection ~ 4750 4650
Wire Wire Line
	4750 4650 5050 4650
Wire Wire Line
	4450 4250 4450 4650
Connection ~ 4450 4650
Wire Wire Line
	4450 4650 4750 4650
Wire Wire Line
	4750 3950 4750 3450
Connection ~ 4750 3450
Wire Wire Line
	4750 3450 4950 3450
Wire Wire Line
	4450 3950 4450 3450
Connection ~ 4450 3450
Wire Wire Line
	4450 3450 4750 3450
$Comp
L Device:R R7
U 1 1 611E9860
P 5050 4300
F 0 "R7" H 4900 4350 50  0000 L CNN
F 1 "2K2" H 4850 4250 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 4980 4300 50  0001 C CNN
F 3 "~" H 5050 4300 50  0001 C CNN
	1    5050 4300
	-1   0    0    1   
$EndComp
$Comp
L Device:R R6
U 1 1 611E9FB4
P 5050 3250
F 0 "R6" H 5100 3300 50  0000 L CNN
F 1 "10K" H 5100 3200 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 4980 3250 50  0001 C CNN
F 3 "~" H 5050 3250 50  0001 C CNN
	1    5050 3250
	-1   0    0    1   
$EndComp
Wire Wire Line
	5050 4450 5050 4650
Connection ~ 5050 4650
Wire Wire Line
	5050 4650 5350 4650
Wire Wire Line
	5050 3400 5050 3650
Wire Wire Line
	5050 3100 5050 3000
Wire Wire Line
	5050 3000 5150 3000
Connection ~ 5150 3000
$Comp
L Device:C C9
U 1 1 6120C252
P 5350 4300
F 0 "C9" H 5465 4346 50  0000 L CNN
F 1 "0.1uf" H 5465 4255 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder" H 5388 4150 50  0001 C CNN
F 3 "~" H 5350 4300 50  0001 C CNN
	1    5350 4300
	1    0    0    -1  
$EndComp
$Comp
L Device:D_Zener D9
U 1 1 61212685
P 5750 4300
F 0 "D9" V 5704 4379 50  0000 L CNN
F 1 "3V9" V 5795 4379 50  0000 L CNN
F 2 "Diode_SMD:D_MicroMELF_Handsoldering" H 5750 4300 50  0001 C CNN
F 3 "~" H 5750 4300 50  0001 C CNN
	1    5750 4300
	0    1    1    0   
$EndComp
Wire Wire Line
	5350 4150 5350 4050
Wire Wire Line
	5350 4050 5050 4050
Connection ~ 5050 4050
Wire Wire Line
	5050 4050 5050 4150
Wire Wire Line
	5350 4050 5750 4050
Wire Wire Line
	5750 4050 5750 4150
Connection ~ 5350 4050
Wire Wire Line
	5750 4450 5750 4650
Connection ~ 5750 4650
Wire Wire Line
	5750 4650 6100 4650
Wire Wire Line
	5350 4450 5350 4650
Connection ~ 5350 4650
Wire Wire Line
	5350 4650 5750 4650
Wire Wire Line
	3750 3650 5050 3650
Connection ~ 5050 3650
Wire Wire Line
	5050 3650 5050 4050
$Comp
L pja_1:MCP9700 U4
U 1 1 612488DA
P 4300 2700
F 0 "U4" H 4528 2551 50  0000 L CNN
F 1 "MCP9700" H 4528 2460 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92" H 4300 2700 50  0001 C CNN
F 3 "" H 4300 2700 50  0001 C CNN
	1    4300 2700
	1    0    0    -1  
$EndComp
Wire Wire Line
	4000 2800 3700 2800
Wire Wire Line
	2700 2800 2700 3050
Wire Wire Line
	3950 3000 3950 3200
Connection ~ 3950 3550
Wire Wire Line
	3950 3000 4000 3000
Wire Wire Line
	3950 4650 4100 4650
Wire Wire Line
	3750 3750 3850 3750
Wire Wire Line
	3850 3750 3850 2900
Wire Wire Line
	3850 2900 4000 2900
$Comp
L Device:D_Zener D7
U 1 1 6134AB88
P 4100 4100
F 0 "D7" V 4054 4179 50  0000 L CNN
F 1 "3V9" V 4145 4179 50  0000 L CNN
F 2 "Diode_SMD:D_MicroMELF_Handsoldering" H 4100 4100 50  0001 C CNN
F 3 "~" H 4100 4100 50  0001 C CNN
	1    4100 4100
	0    1    1    0   
$EndComp
$Comp
L Device:C C6
U 1 1 6134B549
P 3650 4100
F 0 "C6" H 3700 4300 50  0000 L CNN
F 1 "0.1uf" H 3700 4200 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder" H 3688 3950 50  0001 C CNN
F 3 "~" H 3650 4100 50  0001 C CNN
	1    3650 4100
	1    0    0    -1  
$EndComp
Wire Wire Line
	4100 4250 4100 4650
Connection ~ 4100 4650
Wire Wire Line
	4100 4650 4450 4650
Wire Wire Line
	3650 4250 3650 4650
Connection ~ 3650 4650
Wire Wire Line
	3650 4650 3350 4650
Wire Wire Line
	3650 3950 4100 3950
Wire Wire Line
	4100 3950 4100 3750
Wire Wire Line
	4100 3750 3850 3750
Connection ~ 4100 3950
Connection ~ 3850 3750
$Comp
L Device:R R5
U 1 1 61384743
P 4700 4750
F 0 "R5" H 4770 4796 50  0000 L CNN
F 1 "DNF" H 4770 4705 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 4630 4750 50  0001 C CNN
F 3 "~" H 4700 4750 50  0001 C CNN
	1    4700 4750
	0    1    1    0   
$EndComp
Wire Wire Line
	4850 4750 4950 4750
Connection ~ 4950 4750
Wire Wire Line
	4550 4750 4450 4750
Wire Wire Line
	4450 4750 4450 4650
Text GLabel 1650 4650 0    60   Input ~ 0
GND
$Comp
L Device:R R12
U 1 1 61442EAD
P 6700 4450
F 0 "R12" V 6750 4550 50  0000 L CNN
F 1 "100K" V 6850 4450 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 6630 4450 50  0001 C CNN
F 3 "~" H 6700 4450 50  0001 C CNN
	1    6700 4450
	0    1    1    0   
$EndComp
Wire Wire Line
	6550 4450 6450 4450
Wire Wire Line
	6450 4450 6450 4650
Connection ~ 6450 4650
Wire Wire Line
	6450 4650 7350 4650
Wire Wire Line
	6850 4450 7050 4450
Wire Wire Line
	7050 4450 7050 4300
Wire Wire Line
	7050 4300 6850 4300
$Comp
L Device:R R10
U 1 1 61473A48
P 6250 4300
F 0 "R10" H 6300 4400 50  0000 L CNN
F 1 "100K" H 6300 4300 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 6180 4300 50  0001 C CNN
F 3 "~" H 6250 4300 50  0001 C CNN
	1    6250 4300
	1    0    0    -1  
$EndComp
Wire Wire Line
	6250 4450 6250 4650
Wire Wire Line
	6100 4650 6250 4650
Connection ~ 6250 4650
Wire Wire Line
	6250 4650 6450 4650
Wire Wire Line
	6250 4150 6250 3850
Wire Wire Line
	5650 3850 5650 3650
Wire Wire Line
	5650 3650 5800 3650
$Comp
L Device:Q_NJFET_GSD Q3
U 1 1 6152F878
P 6000 3650
F 0 "Q3" H 6190 3696 50  0000 L CNN
F 1 "2N7002" H 6190 3605 50  0000 L CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 6200 3750 50  0001 C CNN
F 3 "~" H 6000 3650 50  0001 C CNN
	1    6000 3650
	1    0    0    -1  
$EndComp
Wire Wire Line
	5650 3850 6100 3850
$Comp
L Device:Q_NJFET_GSD Q4
U 1 1 61536009
P 7250 4450
F 0 "Q4" H 7440 4496 50  0000 L CNN
F 1 "2N7002" H 7440 4405 50  0000 L CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 7450 4550 50  0001 C CNN
F 3 "~" H 7250 4450 50  0001 C CNN
	1    7250 4450
	1    0    0    -1  
$EndComp
Connection ~ 7050 4450
$Comp
L Device:Q_PJFET_GDS Q6
U 1 1 6154DCA4
P 7650 3950
F 0 "Q6" H 7840 3996 50  0000 L CNN
F 1 "DMP3099L-7" H 7840 3905 50  0000 L CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 7850 4050 50  0001 C CNN
F 3 "~" H 7650 3950 50  0001 C CNN
	1    7650 3950
	1    0    0    -1  
$EndComp
Text Label 9000 3300 0    60   ~ 0
Load2
Text Label 9000 4350 0    60   ~ 0
Load1
$Comp
L Connector:Conn_01x01_Male J9
U 1 1 610235F4
P 9500 5000
F 0 "J9" H 9472 4932 50  0000 R CNN
F 1 "To Shunt Resistor" H 9472 5023 50  0000 R CNN
F 2 "MountingHole:MountingHole_2.5mm_Pad_Via" H 9500 5000 50  0001 C CNN
F 3 "~" H 9500 5000 50  0001 C CNN
	1    9500 5000
	-1   0    0    1   
$EndComp
Wire Wire Line
	9300 5000 9200 5000
Wire Wire Line
	9200 5000 9200 4750
Connection ~ 9200 4750
Wire Wire Line
	9200 4750 9300 4750
$Comp
L Device:R R11
U 1 1 6103912E
P 6650 3950
F 0 "R11" H 6720 3996 50  0000 L CNN
F 1 "100K" H 6720 3905 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 6580 3950 50  0001 C CNN
F 3 "~" H 6650 3950 50  0001 C CNN
	1    6650 3950
	0    1    1    0   
$EndComp
Text GLabel 6850 4300 0    60   Input ~ 0
L1
$Comp
L Device:R R15
U 1 1 6107A5B3
P 7500 3750
F 0 "R15" H 7570 3796 50  0000 L CNN
F 1 "100K" H 7570 3705 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 7430 3750 50  0001 C CNN
F 3 "~" H 7500 3750 50  0001 C CNN
	1    7500 3750
	-1   0    0    1   
$EndComp
$Comp
L Device:R R16
U 1 1 6107BA4E
P 7800 4600
F 0 "R16" H 7600 4650 50  0000 L CNN
F 1 "100K" H 7550 4550 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder" V 7730 4600 50  0001 C CNN
F 3 "~" H 7800 4600 50  0001 C CNN
	1    7800 4600
	-1   0    0    1   
$EndComp
Connection ~ 7800 4750
Wire Wire Line
	7800 4750 7600 4750
Wire Wire Line
	7800 4450 7800 4400
Connection ~ 7800 4400
Wire Wire Line
	7800 4400 7750 4400
Wire Wire Line
	7500 3900 7500 4650
Wire Wire Line
	7500 4650 7600 4650
Wire Wire Line
	7600 4650 7600 4750
Connection ~ 7600 4750
Wire Wire Line
	7600 4750 7550 4750
Wire Wire Line
	7500 3600 7500 3550
$Comp
L Device:C C7
U 1 1 61118EB3
P 3700 3000
F 0 "C7" H 3550 3150 50  0000 L CNN
F 1 "0.1uf" H 3450 2900 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder" H 3738 2850 50  0001 C CNN
F 3 "~" H 3700 3000 50  0001 C CNN
	1    3700 3000
	1    0    0    -1  
$EndComp
Wire Wire Line
	3700 3150 3700 3200
Wire Wire Line
	3700 3200 3950 3200
Connection ~ 3950 3200
Wire Wire Line
	3950 3200 3950 3550
Wire Wire Line
	3700 2850 3700 2800
Connection ~ 3700 2800
Wire Wire Line
	3700 2800 2700 2800
Connection ~ 7500 3000
Wire Wire Line
	5150 3000 7500 3000
$Comp
L Device:Q_PJFET_GDS Q5
U 1 1 61545693
P 7400 3200
F 0 "Q5" H 7590 3246 50  0000 L CNN
F 1 "DMP3099L-7" H 7590 3155 50  0000 L CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 7600 3300 50  0001 C CNN
F 3 "~" H 7400 3200 50  0001 C CNN
	1    7400 3200
	1    0    0    -1  
$EndComp
Connection ~ 7500 3550
Wire Wire Line
	7500 3550 7500 3400
Wire Wire Line
	7500 3000 7750 3000
Wire Wire Line
	7750 3750 7750 3000
Wire Wire Line
	7750 4400 7750 4150
$Comp
L Diode:1N4004 D10
U 1 1 613F4882
P 8050 2750
F 0 "D10" H 8200 2700 50  0000 C CNN
F 1 "1N4004" H 8100 2850 50  0000 C CNN
F 2 "Diode_SMD:D_MELF" H 8050 2575 50  0001 C CNN
F 3 "http://www.vishay.com/docs/88503/1n4001.pdf" H 8050 2750 50  0001 C CNN
	1    8050 2750
	1    0    0    -1  
$EndComp
$Comp
L Diode:1N4004 D11
U 1 1 613F916C
P 8050 3000
F 0 "D11" H 8200 2950 50  0000 C CNN
F 1 "1N4004" H 8100 3100 50  0000 C CNN
F 2 "Diode_SMD:D_MELF" H 8050 2825 50  0001 C CNN
F 3 "http://www.vishay.com/docs/88503/1n4001.pdf" H 8050 3000 50  0001 C CNN
	1    8050 3000
	1    0    0    -1  
$EndComp
Wire Wire Line
	7900 3000 7850 3000
Connection ~ 7750 3000
Wire Wire Line
	7900 2750 7850 2750
Wire Wire Line
	7850 2750 7850 3000
Connection ~ 7850 3000
Wire Wire Line
	7850 3000 7750 3000
Wire Wire Line
	8200 3000 8450 3000
Wire Wire Line
	8450 3000 8450 3300
Connection ~ 8450 3300
Wire Wire Line
	8450 3300 9300 3300
Wire Wire Line
	8200 2750 8700 2750
Wire Wire Line
	8700 2750 8700 4200
Connection ~ 8700 4200
Wire Wire Line
	1650 4650 2900 4650
Text GLabel 2600 3050 0    50   Input ~ 0
VCC
Connection ~ 6100 3850
Wire Wire Line
	6100 3850 6250 3850
Text GLabel 5050 3000 0    50   Input ~ 0
VIN
Text GLabel 2950 3550 0    50   Input ~ 0
SCL
Text GLabel 2950 3650 0    50   Input ~ 0
SDA
Wire Wire Line
	8200 4750 8900 4750
Text GLabel 8700 4750 0    50   Input ~ 0
SHUNT
$EndSCHEMATC