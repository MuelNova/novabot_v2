from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    APEXLEGEND_API_KEY = ""  # https://portal.apexlegendsapi.com/settings


APEXLEGEND_PRED_URL = "https://api.mozambiquehe.re/predator?auth="


