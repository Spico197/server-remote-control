from .inspur import InspurAPI
from .inspur_plain import InspurPlainAPI
from .megapoint import MegapointAPI


API_MAP = {
    "inspur": InspurAPI,
    "supermicro": InspurAPI,
    "inspur_plain": InspurPlainAPI,
    "megapoint": MegapointAPI,
}
