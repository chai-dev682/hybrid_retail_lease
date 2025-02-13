from pydantic import BaseModel
from datetime import date

class RetailLease(BaseModel):
    id: int
    start_date: date
    expiry_date: date
    current_rent_pa: float
    current_rent_sqm: float
    centre_name: str
    tenant_category: str
    tenant_subcategory: str
    lessor: str
    lessee: str
    area: float

    class Config:
        from_attributes = True