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
import ComfeePool



def main():
    
    # Configuration of the Shelly device
    config = ComfeePool.ComfeeConfig(sys.argv[1])
    params_Comfee = config.read(section="comfee")
    params_broker = config.read(section="broker")

    print(f"Comfee Devices Pool Version {ComfeePool.__version__}")
    print(f"Creating Pool of Comfee Devices . . . ", end="")
    pool = ComfeePool.ComfeePool(username=params_Comfee['username'], password=params_Comfee['password'], brokerIP=params_broker['ip'], brokerPort=int(params_broker['port']))
    print(f"[ OK ]")

    print(f"Connecting the pool")
    pool.connect()
    print(f"Discovering devices")
    pool.discover()

    print(f"Running the pool")
    pool.start()
    
    print(f"Finalizing Comfee Pool . . . [ OK ]")
    

if __name__ == "__main__":
    main()
