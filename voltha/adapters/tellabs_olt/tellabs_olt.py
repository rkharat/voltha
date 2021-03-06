# Copyright 2018-present Tellabs, Inc.
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
#

"""
Tellabs OLT Adapter for tlabvolt4, tlabvolt8, tlabvolt16, & tlabvolt32
"""
import structlog
from copy import deepcopy

from voltha.protos.device_pb2 import DeviceType
from voltha.protos.adapter_pb2 import AdapterConfig
from voltha.protos.adapter_pb2 import Adapter
from voltha.protos.common_pb2 import LogLevel
from voltha.adapters.openolt.openolt import OpenoltAdapter, OpenOltDefaults
from voltha.adapters.openolt.openolt_device import OpenoltDevice
from voltha.adapters.tellabs_olt.tellabs_resource_manager import TellabsResourceManager

log = structlog.get_logger()

class TellabsAdapter(OpenoltAdapter):
    name = 'tellabs_olt'

    supported_device_types = [
        DeviceType(
            id=name,
            adapter=name,
            accepts_bulk_flow_update=True,
            accepts_direct_logical_flows_update=True
        )
    ]

    def __init__(self, adapter_agent, config):
        super(TellabsAdapter, self).__init__(adapter_agent, config)

        # overwrite the descriptor
        self.descriptor = Adapter(
            id=self.name,
            vendor='Tellabs Inc.',
            version='0.1',
            config=AdapterConfig(log_level=LogLevel.INFO)
        )

        log.info('tellabs_olt.__init__', adapter=self.descriptor)

    def adopt_device(self, device):
        log.info('adopt-device', device=device)

        support_classes = deepcopy(OpenOltDefaults)['support_classes']

        # Customize resource_mgr
        support_classes['resource_mgr'] = TellabsResourceManager

        kwargs = {
            'support_classes': support_classes,
            'adapter_agent': self.adapter_agent,
            'device': device,
            'device_num': self.num_devices + 1
        }
        try:
            self.devices[device.id] = OpenoltDevice(**kwargs)
        except Exception as e:
            log.error('Failed to adopt OpenOLT device', error=e)
            del self.devices[device.id]
            raise
        else:
            self.num_devices += 1
