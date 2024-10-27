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
import YeelightPool



def main():
    
    # Configuration of the Shelly device
    config = YeelightPool.YeelightConfig(sys.argv[1])
    params_yeelight = config.read(section="yeelight")
    params_broker = config.read(section="broker")

    print(f"Yeelight Devices Pool Version {YeelightPool.__version__}")
    print(f"Creating Pool of Yeelight Devices . . . ", end="")
    pool = YeelightPool.YeelightPool(params_broker['ip'], int(params_broker['port']))
    print(f"[ OK ]")

    print(f"Running the pool")
    pool.start(
        eval(params_yeelight['lamps']), 
        eval(params_yeelight['room']), 
        eval(params_yeelight['device'])
        )
    
    print(f"Finalizing Yeelight Pool . . . [ OK ]")
    

if __name__ == "__main__":
    main()
