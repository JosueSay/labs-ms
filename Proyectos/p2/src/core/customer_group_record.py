from dataclasses import dataclass
from core.mm1_model import CustomerRecord

@dataclass
class CustomerGroupRecord(CustomerRecord):
    group_size: int = 1
