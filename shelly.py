# TheBlackmad
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import ShellyPool



def main():
    
    # Configuration of the Shelly device
    config = ShellyPool.ShellyConfig(sys.argv[1])
    params_shelly = config.read(section="shelly")
    params_broker = config.read(section="broker")

    print(f"Shelly Devices Pool Version {ShellyPool.__version__}")
    print(f"Creating Pool of Shelly Devices . . . ", end="")
    pool = ShellyPool.ShellyPool(params_broker['ip'], int(params_broker['port']))
    print(f"[ OK ]")

    print(f"Running the pool")
    pool.start(
        eval(params_shelly['topic']), 
        eval(params_shelly['room']), 
        eval(params_shelly['device'])
        )
    
    print(f"Finalizing Shelly Pool . . . [ OK ]")
    

if __name__ == "__main__":
    main()


