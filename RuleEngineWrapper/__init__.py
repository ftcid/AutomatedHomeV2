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
import logging
import sys
import ast
import os
import time
import threading

import yaml
import rule_engine

class RuleEngineWrapper:
    """ Wrapper for the rule-engine library so it can work with MQTT topics strings
    like /<level0>/<level1>/attribute"""
    def __init__(self, yaml_file:str,
                log_to_file: bool = False, log_file: str = "RuleEngineWrapper.log",
				debug: bool = False):
        """Initialize the RuleEngineWrappe.

        Args:
            yaml_file (str): YAML file with rules.
            log_to_file (bool): Whether to log to a file.
            log_file (str): Name of the log file.
            debug (bool): Whether to enable debug-level logging.
        """
        self.debug = debug
        self.log_to_file = log_to_file
        self.log_file = log_file

        self._setup_logging()

        # read the rules file. Running in a thread allows to update the rules file 
        # without having to restart the system.
        self.yaml_file = yaml_file
        self.last_modified_time = None
        #self.rules = self.load_rules()      
        self.rules = None  
        self.rules_file_watcher_id = threading.Thread(target=self.load_and_run, name='rules_file_watcher', daemon=True)
        self.rules_file_watcher_id.start()
        

    def load_rules(self):
        """Load rules from the YAML file."""
        rules = None
        text_rules = ''
        try:
            if self.yaml_file is not None:
                with open(self.yaml_file, 'r') as file:
                    rules = yaml.safe_load(file)['rules']
                    for rule in rules:
                        text_rules = f"{text_rules}\n{rule}"

        except Exception as e:
            logging.error(f"Exception: {e}")

        logging.info(f"RULES: {text_rules}")
        return rules
            
            
    def load_and_run(self):
        while True:
            try:
                current_modified_time = os.path.getmtime(self.yaml_file)
            except FileNotFoundError:
                logging.error(f"File {self.yaml_file} not found.")
                
            if self.last_modified_time is None or current_modified_time != self.last_modified_time:
                logging.info(f"File {self.yaml_file} has been modified. Reloading data.")
                self.rules = self.load_rules()
                self.last_modified_time = current_modified_time
                
            time.sleep(60)


    def _setup_logging(self):
        """Sets up the logging configuration for the class."""
        if self.log_to_file:
            logging.basicConfig(filename=self.log_file, level=logging.DEBUG if self.debug else logging.INFO)
        else:
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if self.debug else logging.INFO)


    def _preprocess_rule(self, rule_str):
        """Preprocess rule by replacing '/' with '_' in rule string.
        
        Args:
            rule_str (str): rule to preprocess
            
        Returns:
            str: preprocessed rule
        """
        return rule_str.replace('/', '_')
        

    def _preprocess_data(self, data):
        """Preprocess data by replacing '/' with '_' in keys.
        
        Args:
            data (dict): data dictionary to preprocess ({'topic': 'value'})
            
        Returns:
            dict: preprocessed data
        """
        return {key.replace('/', '_'): self.get_var(value) for key, value in data.items()}
        

    def _is_int(self, s):
        """Check whether a string can be represented as integer.
        
        Args:
            s (str): string
            
        Returns:
            bool: True/False
        """
        if type(s)==int:
            return True

        elif type(s)==str and len(s)>0:
            try:
                int_value = int(s)
            except ValueError:
                return False
            return '.' not in s and 'e' not in s

        return False


    def _is_float(self, s):
        """Check whether a string can be represented as float.
        
        Args:
            s (str): string
            
        Returns:
            bool: True/False
        """        
        if type(s)==float:
            return True

        elif type(s)==str and len(s)>0:
            try:
                float_value = float(s)
            except ValueError:
                return False
            return '.' in s or 'e' in s.lower()   
        return False                                  


    def _is_bool(self, s):
        """Check whether a string can be represented as bool.
        
        Args:
            s (str): string
            
        Returns:
            bool: True/False
        """        
        if type(s)==bool:
            return True
            
        elif type(s)==str and len(s)>0:
            if s.lower() in ["true", "false"]:
                return True

        return False


    def _is_dict(self, s):
        """Check whether a string can be represented as dictionary.
        
        Args:
            s (str): string
            
        Returns:
            bool: True/False
        """        
        if type(s)==dict:
            return True
            
        elif type(s)==str:
            try:
                dict_value = ast.literal_eval(s)
            except ValueError:
                return False
            except SyntaxError: # this error in case len(s)==0
                return False

        return True
        

    def get_var(self, s):
        """Returns the represented value of a string.
        
        Args:
            s (str): string
            
        Returns:
            int/float/bool/dict/str: depending on the represented value 
        """
        if self._is_int(s):
            return int(s)
            
        elif self._is_float(s):
            return float(s)
            
        elif self._is_bool(s):
            return True if s.lower() == "true" else False
            #return {"true": True, "false": False}
            
        elif self._is_dict(s):
            return ast.literal_eval(s)
            
        return s


    def evaluate_rules(self, data, rule_filter=''):                
        """Evaluate rules from the YAML file on the given data.

        Args:
            data (dict): data to check against the rules
            rule_filter (str): rules to check against, so not all rules will be checked
            
        Returns:
            list: list of actions in the form of dictionaries
        """
        output = []

        logging.debug(f"DATA: {data}\n\n")
        logging.debug(f"RULES: {self.rules}\n\n")
        # there are rules to check!
        if self.rules is not None:
            
            try:
                # Preprocess data for compatibility
                logging.debug(f"PREPROCESS DATA: {data}\n LENGHT of data: {len(data)}\n\n")
                preprocessed_data = self._preprocess_data(data)

                # Iterate over each rule in the YAML file
                for rule_info in self.rules:
                    # Preprocess the rule
                    logging.debug(f"PREPROCESS RULE {rule_info['rule']}\n\n")
                    rule_str = self._preprocess_rule(rule_info['rule'])
                    actions = rule_info['actions']

                    try:
                        logging.debug(f"PREPROCESS RULE_FILTER {rule_filter if rule_filter != '' else None}\n\n")
                        if self._preprocess_rule(rule_filter) in rule_str:
                            # Create the rule object
                            logging.debug(f"RULE_ENGINE.RULE {rule_str}\n\n")
                            rule = rule_engine.Rule(rule_str)

                            # Evaluate the rule
                            if rule.matches(preprocessed_data):
                                # If rule matches, perform the associated actions
                                logging.debug(f"MATCHES - COLLECTING ACTIONS\n\n")
                                for action in actions:
                                    output.append(action)

                    except rule_engine.errors.RuleSyntaxError as e:
                        # Handle rule syntax errors
                        logging.error(f"Rule syntax error in rule '{rule_str}': {e}")
                    except rule_engine.errors.SymbolResolutionError as e:
                        # Handle rule not found
                        logging.info(f"Not found the rule topic {e}")
                        
            except Exception as e:
                logging.error(f"Unexpected Error during rule evaluation: {e}")
                
        return output
