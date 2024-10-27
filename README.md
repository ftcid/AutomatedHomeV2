# AutomatedHomeV2
AutomatedHome is a from scratch version of AutomatedHome based mainly in Python. It is developed to integrate devices in MQTT based environment.

**Note: this is the normal evolution of the AutomatedHome project initially written in C++ (https://github.com/ftcid/AutomatedHome)**

This intend to integrate several devices such as lamps, temperature, humidity sensors, dehumidifiers, etc. into one system for monitor an control automatically.

Devices supported:

  - Shelly devices (/shelly) for power control. It provided to published topics information about the status of the device, as well as receives commands through MQTT topics.
  - Midea devices for control of the dehumidification devies. It provides status of the device as well as receives commands through MQTT Topics.
  - Yeelight device for grouping bulbs into lamps and control of light configurations through MQTT messages. It provides status and can react to commands via MQTT Messages.
  - DHT22 (/DHT22v2) devices provides temperature and humidity measurements. Values are read from a NodeMCU (ESP12E Module) board, and values published in the MQTT Broker given in the .h file.

All modules connect to an MQTT Broker to exchange messages. Events are triggered by update to the topics subscribed or published.

Next steps include monitor and control of Yeelight equipment, Dehumidifiers from Comfee, DIY sensors for temperature and humidifiers, notifications tool over Telegram and any other function that may be useful.

## How to use
To use this system, the first thing to do is configure the modules. Each module is a program that runs and uses the python libraries created to manage the devices. The libraries creates an MQTT interface to the device so it can be operated and monitored by the main program, ___ah_master.py___.

The config files for each libraries basically contains information about the connection to the broker, passwords to connect to Cloud System of the device and information about how to organize the devices in the MQTT tree of topics.

As the general rule, the devices will be located in the form of ___\/<level0>\/<level1\/<attribute>___ where
- ___<level0>___ is generally the room where the devices is located (eg.- living room)
- ___<level1>___ is generally the device name in the room /(eg.- ceiling lamp)
- ___<attribute>___ is the attribute for this device (eg.- power on/off)

The system has an script to start all module programs and the master. This script is called ___automatedhomev2.sh___. Please follow the help in this script to get further information about how to use it.

## How to use the rule system
The system has a mechanism to operate with rules. The file ___rules.yaml___ provides an example on how to generate actions on a module based upon this file. The rule engine is used from the library ___rule_engine___. This engine is wrapped in a class to permit use it with topics with the character '/', as this is a special character for the ___rule_engine___ library.

## Release Notes
0.1.1 - First version. A predecessor project is used as the basis idea for developing this project further. This can be found under https://github.com/ftcid/AutomatedHome.

## Requirements
This project could be made possible thanks to the following libraries: 
- ComfeePool - https://github.com/ftcid/ComfeePool
- ShellyPool - https://github.com/ftcid/ShellyPool
- YeelightPool - https://github.com/ftcid/YeelightPool

Also the requirements.txt file contains the external libraries used.
