sql_vector = """
You need to select one proper database to gather information that related to following query.

The query is as follows.
{query}

This query is generated based on the conversation between user and assistant, and will be used to gather relevant information to generate response to user's question.
Here is the original conversation.
{conversation}

We have two databases.
One is MySQL Database and the other one is Pinecone Vector Database.
MySQL Database includes structured information about the retail leases.
You need to search via those retail leases.
Here is SQL Query that is used to create table.
```
CREATE TABLE IF NOT EXISTS retail_leases (
  id INT PRIMARY KEY,
  start_date DATE,
  expiry_date DATE,
  current_rent_pa DECIMAL(10,2), -- Annual rent in thousands
  current_rent_sqm DECIMAL(10,2), -- Rent per square meter
  centre_name VARCHAR(255),
  tenant_category VARCHAR(255),
  tenant_subcategory VARCHAR(255),
  lessor VARCHAR(255),
  lessee VARCHAR(255),
  area DECIMAL(10,2) -- Leased area in square meters
);
```

Pinecone VectorDB includes some general information about the retail leases.
If user wanna search or know about the retail leases or something related to that, you need to select Pinecone VectorDB.
And if user is asking some sql related questions like how much, please select MySQL Database.
"""