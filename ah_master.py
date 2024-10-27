# TheBlackmad
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import paho.mqtt.client as mqtt
import threading
import json
import datetime
import time
import ast
import queue
from RuleEngineWrapper import RuleEngineWrapper

from flask import Flask, request, jsonify
import requests
import random, string
import socket


"""
Automated Home System Master

This module implements the core of an automated home system using MQTT for communication,
Flask for web interactions, and threading for concurrency. The system listens for device
status updates via MQTT, exposes the current state of devices through a web API, and 
manages a simple database interface to store data.

Classes:
    - AutomatedHomeMaster: Central controller class managing MQTT, web, and DB interfaces.
    - MQTTInterface: Manages MQTT communication, subscribing to topics, and handling messages.
    - JSONWebInterface: Exposes the automated home system's data through a Flask-based web API.
    - DBInterface: Simulates database operations for storing device status updates.
"""

class AutomatedHomeMaster:
    """
    Central controller for the Automated Home System.

    Attributes:
        broker_host (str): The MQTT broker host.
        broker_port (int): The MQTT broker port.
        topic (str): The MQTT topic to subscribe to (default: '#').
        messages (dict): A dictionary storing the latest message from each MQTT topic.
        db_queue (queue.Queue): Queue for storing data to be processed by the DB interface.
        stop_event (threading.Event): An event flag to control the shutdown of threads.
        mqtt_interface (MQTTInterface): The MQTT interface instance.
        web_interface (JSONWebInterface): The web interface instance for external interactions.
        db_interface (DBInterface): The database interface instance.
    """
    
    def __init__(self, broker_host: str = '127.0.0.1', broker_port: int = 1883, topic: str = '#', rules_yaml: str = None):
        """
        Initializes the AutomatedHomeMaster class.

        Args:
            broker_host (str): MQTT broker address (default: '127.0.0.1').
            broker_port (int): MQTT broker port (default: 1883).
            topic (str): Topic to subscribe to (default: '#', wildcard for all topics).
        """
        self.messages = {}
        self.db_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.rules_yaml = rules_yaml
        self.rule_engine = None
        
        # Initialize interfaces for MQTT, Web API, and Database
        self.rule_engine = RuleEngineWrapper(rules_yaml)
        self.mqtt_interface = MQTTInterface(broker_host, broker_port, topic, self.messages, self.db_queue, self.stop_event, self.rule_engine)
        self.web_interface = JSONWebInterface(self.messages, self.stop_event)
        self.db_interface = DBInterface(self.db_queue, self.stop_event)
        
        
    def start(self):
        """
        Starts the system by launching MQTT, web, and database interfaces in separate threads.
        It also handles the shutdown logic when a stop signal is triggered.
        """
        # Create and start threads for each interface
        self.mqtt_if_thread = threading.Thread(target=self.mqtt_interface.start, name='mqtt_interface')
        self.web_if_thread = threading.Thread(target=self.web_interface.start, args=('host', 7900, False), name='web_interface')
        self.db_if_thread = threading.Thread(target=self.db_interface.start, name='db_interface')
        
        self.mqtt_if_thread.start()
        self.web_if_thread.start()
        self.db_if_thread.start()

        
        try:
            # Main loop to keep the system running until a stop signal is received
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        
        # Wait for threads to finish
        print(f"Stopping mqtt thread . . . ", end="")
        self.mqtt_if_thread.join()
        print(f"[ OK ]\nStopping web thread . . . ", end="")
        self.web_if_thread.join()
        print(f"[ OK ]\nStopping db thread . . . ",end="")
        self.db_if_thread.join()
        print(f"[ OK ]")
        
        
    def stop(self):
        """
        Triggers the stop event to gracefully shutdown all threads.
        """
        print("Stopping AutomatedHome System...")
        self.stop_event.set()



class MQTTInterface:
    """
    Interface for handling MQTT communication.

    Attributes:
        broker_host (str): MQTT broker host.
        broker_port (int): MQTT broker port.
        topic (str): Topic to subscribe to.
        messages (dict): Dictionary storing the latest message for each topic.
        db_queue (queue.Queue): Queue to store messages for the database interface.
        stop_event (threading.Event): Event to signal when to stop the interface.
        client (mqtt.Client): The MQTT client instance.
    """
    
    def __init__(self, broker_host: str, broker_port: int, topic: str, messages: dict, db_queue: queue.Queue, stop_event: threading.Event, rule_engine: RuleEngineWrapper = None, topic_ping:str='/global/ping/devices'):
        """
        Initializes the MQTTInterface class.

        Args:
            broker_host (str): MQTT broker host.
            broker_port (int): MQTT broker port.
            topic (str): MQTT topic to subscribe to.
            messages (dict): A dictionary to store messages.
            db_queue (queue.Queue): A queue for database processing.
            stop_event (threading.Event): Event for stopping the MQTT loop.
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.topic_ping = topic_ping
        self.messages = messages
        self.ping = {}
        self.db_queue = db_queue
        self.publish_queue = queue.Queue()
        self.stop_event = stop_event
        self.rule_engine = rule_engine
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when the MQTT client successfully connects to the broker.

        Args:
            client: MQTT client instance.
            userdata: User-defined data of any type (not used).
            flags: Response flags sent by the broker.
            rc: Connection result code.
        """
        print(f"Connected to MQTT Broker with result code {rc}")
        client.subscribe(self.topic)
        

    def on_message(self, client, userdata, msg):
        """
        Callback when a message is received on a subscribed topic.

        Args:
            client: MQTT client instance.
            userdata: User-defined data of any type (not used).
            msg: The received MQTT message.
        """
        try:
            payload = msg.payload.decode()
            print(f"Received message on {msg.topic}: {payload}")
            
            if not msg.topic.startswith('/'):
                return 
            
            if ( msg.topic not in self.messages.keys() ) or ( self.messages[msg.topic] != payload ):
                # Update message dictionary
                self.messages[msg.topic] = payload
                
                # Process rules / conditions
                if self.rule_engine is not None:
                    actions = []
                    actions = self.rule_engine.evaluate_rules(self.messages, msg.topic)
                    
                    for action in actions:
                       # publish the actions through a queue. The start function will publish them later
                       # The reason for doing this is to avoid reentries in the callback
                       action_dict = self.rule_engine.get_var(action)
                       self.publish_queue.put((action_dict['topic'], str(action_dict['params']).replace("\'", "\"")))
                       #self.client.publish(action_dict['topic'], str(action_dict['params']).replace("\'", "\""))
                       
                # For thos messages not in /global/ we do the PING and the database storage
                if not msg.topic.startswith('/global/'):
                                    
                    # Queue message for database processing
                    self.db_queue.put((msg.topic, payload))
                
                    # Register ping (last time alive)
                    if self.topic_ping not in self.messages.keys():
                        self.messages[self.topic_ping] = "{}"
                    ping_dict = ast.literal_eval(self.messages[self.topic_ping])
                    ping_dict[msg.topic.rsplit('/', 1)[0]] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.publish_queue.put((self.topic_ping, str(ping_dict)))
                    #self.client.publish(self.topic_ping, str(self.ping))
            
            
        except Exception as e:
            print(f"Error decoding or queueing message: {e} {msg.topic} /// {payload}")
            
    def start(self):
        """
        Starts the MQTT client, connects to the broker, and begins the message loop.
        It runs until the stop event is triggered.
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_host, self.broker_port, 60)
        
        # Start MQTT loop in the background
        self.client.loop_start()
        while not self.stop_event.is_set():
            try:
                message = self.publish_queue.get(timeout=1)
                self.client.publish(*message)
                #self.stop_event.wait(1)
            except queue.Empty:
                pass
        
        # Stop the loop and disconnect client
        self.client.loop_stop()
        self.client.disconnect()


class JSONWebInterface:
    """
    Flask-based web interface for exposing device data via JSON API.

    Attributes:
        messages (dict): Dictionary holding the latest device messages.
        stop_event (threading.Event): Event to stop the web server.
        host (str): Local IP Address
        port (int): Web service port
        app (Flask): The Flask app instance.
    """
    
    def __init__(self, messages, stop_event):
        """
        Initializes the JSONWebInterface class.

        Args:
            messages (dict): Dictionary to store device status.
            stop_event (threading.Event): Event to stop the web interface.
        """
        self.messages = messages
        self.stop_event = stop_event
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 0
        
        # Initialize Flask app
        self.app = Flask("JSONWebInterface_AutomatedHome")
        
        # Register route for API
        self.app.add_url_rule('/automatedhome', 'web_request', self.web_request, methods=['GET'])
        self.app.add_url_rule('/stop', 'stop_server', self.stop_server, methods=['GET'])


    def start(self, mode: str = 'local', port: int = 7900, debug: bool = True):
        """
        Starts the Flask web server.

        Args:
            mode (str): Network mode ('local' for localhost or 'host' for public access).
            port (int): Port number for the server.
            debug (bool): Debug mode flag.
        """
        if mode == 'host':
            m = '0.0.0.0'
        else:
            m = '127.0.0.1'
        self.port = port
                
        print("Starting JSON Web Interface...")
        self.__app_thread = threading.Thread(target=lambda: self.app.run(host=m, port=port, debug=debug, use_reloader=False)).start()
        
        # Keep running until stop_event is triggered
        while not self.stop_event.is_set():
            time.sleep(1)
            
        # Close the server
        try:
            req = requests.get('http://' + self.host + ':' + str(self.port) + '/stop')
        except Exception as e:
            raise (f"Exception while stopping web server: {e}")
                        

    def stop_server(self):
        """
        Handles GET requests to the '/stop' route.

        Returns:
            JSON response with the result of executing a Flask Server stop.
        """        
        if request.remote_addr == '127.0.0.1':
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            return jsonify({'status': 'OK', 'message': 'Server closed', 'output': None}), 200
            
        else:
            return jsonify({'status': 'Error', 'message': 'Action Forbidden', 'output': None}), 403
        

    def web_request(self):
        """
        Handles GET requests to the '/automatedhome' route.

        Returns:
            JSON response with the result of executing a command.
        """
        try:
            command = request.args.get('command')
            args = {
                'room': request.args.get('room'),
                'device': request.args.get('device')
            }
            result = self.execute_command(command, args)
            return jsonify(result)
        except Exception as e:
            return jsonify({'status': 'Error', 'message': str(e), 'output': None}), 400

    def execute_command(self, command: str, args: dict):
        """
        Executes a command on the automated home system based on the request.

        Args:
            command (str): The command to execute (e.g., list_device).
            args (dict): Command arguments (e.g., room, device).

        Returns:
            dict: Response status and output.
        """
        output = None
        if command == "list_device":
            room = args.get('room')
            device = args.get('device')
            patt = f'/{room}/{device}/'
            for key, value in self.messages.items():
                if key.startswith(patt):
                    output = output or {}
                    output[key] = value
        
        elif command == "list_all_devices":
            patt = '/'
            for key, value in self.messages.items():
                if key.startswith(patt):
                    output = output or {}
                    output[key] = value
        
        else:
            raise Exception("Command not known")
            
        output = self.__get_nested_dict(output)
        return {'output': output, 'status': 'Ok'}
            
    def __get_nested_dict(self, input_dict:dict):
        """
        Provides a nested dictionary based on the input dictionary. The keys of the input
        are the topics in the form /<room>/<device>/<attribute>. The output of the function
        is a dictionary nested (groupped) by <room> and >device>

        Args:
            input_dict (dict): The input dictionary.

        Returns:
            dict: Nested dict.
        """
        nested_dict = {}
    
        for key, value in input_dict.items():
            # Remove leading '/' and split the key into parts: room, device, attribute
            parts = key.lstrip('/').split('/')
            room, device, attribute = parts
            
            # Ensure the room and device exist in the nested dictionary
            if room not in nested_dict:
                nested_dict[room] = {}
            if device not in nested_dict[room]:
                nested_dict[room][device] = {}
            
            # Assign the attribute and its value
            nested_dict[room][device][attribute] = value
        
        return nested_dict


class DBInterface:
    """
    Simulates a database interface to store device statuses.

    Attributes:
        db_queue (queue.Queue): Queue for storing device status updates.
        stop_event (threading.Event): Event to signal when to stop the interface.
    """
    
    def __init__(self, db_queue, stop_event):
        """
        Initializes the DBInterface class.

        Args:
            db_queue (queue.Queue): Queue for storing device data.
            stop_event (threading.Event): Event to stop the DB interface.
        """
        self.db_queue = db_queue
        self.stop_event = stop_event
        
    def start(self):
        """
        Starts the DBInterface to process the queue and store data.
        Simulates the storage process by printing messages.
        """
        print("Starting DB Interface...")
        while not self.stop_event.is_set():
            try:
                topic, status = self.db_queue.get(timeout=1)
                print(f"Storing in DB (dummy): {topic} {status} /// Elements in Queue: {self.db_queue.qsize()}")
                time.sleep(0.1)
            except queue.Empty:
                pass




if __name__ == "__main__":
    # Main entry point of the application
    automatedHome = AutomatedHomeMaster(rules_yaml='rules.yaml')
    automatedHome.start()
    print("Finalizing Automated Home Master...")
