sql_vector = """
You need to select the most appropriate database to gather information related to the following query.

Query: {query}

We have two databases:
1. MySQL Database: Contains structured information about retail leases, good for numerical queries and specific data lookups.
2. Pinecone Vector Database: Contains semantic information about retail leases, good for general information and similarity searches.

Should we use the MySQL database for this query? Answer only 'yes' or 'no'.
Consider using MySQL if the query:
- Asks for specific numerical data
- Requires mathematical operations (averages, sums, counts)
- Needs exact matches or comparisons
"""