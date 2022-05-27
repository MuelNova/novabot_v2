from collections import defaultdict
from typing import Dict, List, Union


class GlobalVar(dict):
    loaded_service: Dict[str, Union["Service", "SchedulerService"]] = {}
    service_bundle: Dict[str, List[Union["Service", "SchedulerService"]]] = defaultdict(list)

    def __setattr__(self, key, value):
        self[key] = value
