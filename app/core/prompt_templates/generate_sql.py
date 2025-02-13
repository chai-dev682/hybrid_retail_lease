generate_sql = """
Generate a MySQL query for the following natural language query.
The database contains retail lease information with the following schema:

CREATE TABLE retail_leases (
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
);

Query: {query}

Generate only the SQL query, nothing else.
Don't include any other text or comments like ```sql or ```\\n
"""