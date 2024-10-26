# AutomatedHomeV2
AutomatedHome is a from scratch version of AutomatedHome based mainly in Python. It is developed to integrate devices in MQTT based environment.

**Note: this is the normal evolution of the AutomatedHome project initially written in C++ (https://github.com/ftcid/AutomatedHome) **

This intend to integrate several devices such as lamps, temperature, humidity sensors, dehumidifiers, etc. into one system for monitor an control automatically.

Devices supported:

  - Shelly devices (/shelly) for power control. It provided to published topics information about the status of the device, as well as receives commands through MQTT topics.
  - Midea devices for control of the dehumidification devies. It provides status of the device as well as receives commands through MQTT Topics.
  - Yeelight device for grouping bulbs into lamps and control of light configurations through MQTT messages. It provides status and can react to commands via MQTT Messages.
  - DHT22 (/DHT22v2) devices provides temperature and humidity measurements. Values are read from a NodeMCU (ESP12E Module) board, and values published in the MQTT Broker given in the .h file.

All modules connect to an MQTT Broker to exchange messages. Events are triggered by update to the topics subscribed or published.

Next steps include monitor and control of Yeelight equipment, Dehumidifiers from Comfee, DIY sensors for temperature and humidifiers, notifications tool over Telegram and any other function that may be useful.
