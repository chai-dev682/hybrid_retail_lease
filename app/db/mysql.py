from sqlalchemy import create_engine
from sqlalchemy import text

from app.core.config import settings
from app.schemas.retail_lease import RetailLease

class MySQLService:
    def __init__(self):
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            url = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"
            self._engine = create_engine(url, pool_pre_ping=True)
        return self._engine

    def initialize(self):
        """Create the retail_leases table if it doesn't exist"""
        engine = self._get_engine()
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS retail_leases (
                    id INT PRIMARY KEY,
                    start_date DATE,
                    expiry_date DATE,
                    current_rent_pa DECIMAL(10,2),
                    current_rent_sqm DECIMAL(10,2),
                    centre_name VARCHAR(255),
                    tenant_category VARCHAR(255),
                    tenant_subcategory VARCHAR(255),
                    lessor VARCHAR(255),
                    lessee VARCHAR(255),
                    area DECIMAL(10,2)
                )
                """))
        finally:
            engine.dispose()

    def insert_lease(self, lease: RetailLease):
        engine = self._get_engine()
        try:
            with engine.connect() as conn:
                sql = text("""INSERT INTO retail_leases 
                        (id, start_date, expiry_date, current_rent_pa, current_rent_sqm,
                         centre_name, tenant_category, tenant_subcategory, lessor, lessee, area)
                        VALUES (:id, :start_date, :expiry_date, :current_rent_pa, :current_rent_sqm,
                               :centre_name, :tenant_category, :tenant_subcategory, :lessor, :lessee, :area)""")
                conn.execute(sql, {
                    "id": lease.id,
                    "start_date": lease.start_date,
                    "expiry_date": lease.expiry_date,
                    "current_rent_pa": lease.current_rent_pa,
                    "current_rent_sqm": lease.current_rent_sqm,
                    "centre_name": lease.centre_name,
                    "tenant_category": lease.tenant_category,
                    "tenant_subcategory": lease.tenant_subcategory,
                    "lessor": lease.lessor,
                    "lessee": lease.lessee,
                    "area": lease.area
                })
                conn.commit()
        finally:
            engine.dispose()

    def query(self, sql: str):
        engine = self._get_engine()
        try:
            with engine.connect() as conn:
                from sqlalchemy import text
                results = conn.execute(text(sql)).fetchall()
                return results
        finally:
            engine.dispose()

mysql_db = MySQLService()