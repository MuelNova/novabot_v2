from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    APEXLEGEND_API_KEY = "3309500fab026da67d8c1db9d8c2cebe"  # https://portal.apexlegendsapi.com/settings


APEXLEGEND_PRED_URL = "https://api.mozambiquehe.re/predator?auth="


