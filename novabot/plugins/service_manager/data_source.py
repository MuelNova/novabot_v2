from typing import Dict, List
from collections import defaultdict


class GlobalVar(dict):
    loaded_service: Dict[str, "Service"] = {}
    service_bundle: Dict[str, List["Service"]] = defaultdict(list)

    def __setattr__(self, key, value):
        self[key] = value
