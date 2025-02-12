from langchain_openai import OpenAIEmbeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import csv
import uuid
from dotenv import load_dotenv
import config
import time
import chardet

from .db_utils import format_date

load_dotenv()

pc = Pinecone(api_key=config.PINECONE_API_KEY)
dims = 3072
spec = ServerlessSpec(
    cloud="aws", region="us-east-1"  # us-east-1
)

# check if index already exists (it shouldn't if this is first time)
existing_indexes = pc.list_indexes()

if config.PINECONE_INDEX_NAME not in [item["name"] for item in existing_indexes]:
    # if does not exist, create index
    print("creating index on pinecone...")
    pc.create_index(
        name=config.PINECONE_INDEX_NAME,
        dimension=dims,
        metric='cosine',
        spec=spec
    )
    # wait for index to be initialized
    while not pc.describe_index(config.PINECONE_INDEX_NAME).status['ready']:
        time.sleep(1)
else:
    print(f"Index with name '{config.PINECONE_INDEX_NAME}' already exists.")
    # user_input = input("Would you like to delete and recreate the index? (y/n): ").lower()
    # if user_input == 'y':
    #     print(f"Deleting index '{config.PINECONE_INDEX_NAME}'...")
    #     pc.delete_index(config.PINECONE_INDEX_NAME)
    #     print("Creating new index...")
    #     pc.create_index(
    #         name=config.PINECONE_INDEX_NAME,
    #         dimension=dims,
    #         metric='cosine',
    #         spec=spec
    #     )
    #     while not pc.describe_index(config.PINECONE_INDEX_NAME).status['ready']:
    #         time.sleep(1)
    #     print("Index recreated successfully!")
    # else:
    #     print("Using existing index.")

def generate_vector_text(record: dict) -> str:
    """Generate a text representation of the record for vector storage"""
    fields = [
        ("CentreName", "Shopping Centre"),
        ("TenantCategory", "Business Category"),
        ("TenantSubCategory", "Business Subcategory"),
        ("Lessor", "Property Owner"),
        ("Lessee", "Tenant")
    ]
    
    text_parts = []
    for field, label in fields:
        if field in record and record[field]:
            text_parts.append(f"{label}: {record[field]}")
    
    return "\n".join(text_parts)

# connect to index
index = pc.Index(config.PINECONE_INDEX_NAME)

embed_model = OpenAIEmbeddings(
    model=config.ModelType.embedding,
    openai_api_key=config.OPENAI_API_KEY
)

# embed and index all our our data!
def import_csv_to_vector(csv_file_path):
    # Detect the file encoding
    with open(csv_file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(csv_file_path, 'r', encoding=encoding) as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        ind = 0

        for row in reader:
            ind = ind + 1
            embedding_id = str(uuid.uuid4())
            cleaned_data = {
                    "id": int(row[2]),
                    "StartDate": format_date(row[6]),
                    "ExpiryDate": format_date(row[7]),
                    "CurrentRentPa": int(row[25]),
                    "CurrentRentSqm": int(row[26]),
                    "CentreName": row[12],
                    "TenantCategory": row[32],
                    "TenantSubCategory": row[33],
                    "Lessor": row[20],
                    "Lessee": row[21],
                    "Area": int(row[17])
                }
            vector = [{
                'id': embedding_id,
                'values':embed_model.embed_documents(generate_vector_text(cleaned_data))[0],
                'metadata': cleaned_data,
            }]
            index.upsert(vectors=vector)
            print(f"row {ind}: done")

    print("CSV data imported successfully into pinecone vector database.")

def format_rag_contexts(matches: list):
    contexts = []
    for x in matches:
        text = (
            f"StartDate: {x['metadata']['StartDate']}\n"
            f"ExpiryDate: {x['metadata']['ExpiryDate']}\n"
            f"CurrentRentPa: {x['metadata']['CurrentRentPa']}\n"
            f"CurrentRentSqm: {x['metadata']['CurrentRentSqm']}\n"
            f"CentreName: {x['metadata']['CentreName']}\n"
            f"TenantCategory: {x['metadata']['TenantCategory']}\n"
            f"TenantSubCategory: {x['metadata']['TenantSubCategory']}\n"
            f"Lessor: {x['metadata']['Lessor']}\n"
            f"Lessee: {x['metadata']['Lessee']}\n"
            f"Area: {x['metadata']['Area']}\n"
        )
        contexts.append(text)
    context_str = "\n---\n".join(contexts)
    return context_str

def query_pinecone(query: str, top_k = 5):
    #query pinecone and return list of records
    xq = embed_model.embed_documents([query])

    # initialize the vector store object
    xc = index.query(
        vector=xq[0], top_k=top_k, include_metadata=True
    )

    context_str = format_rag_contexts(xc["matches"])
    return context_str

# Entry point
# if __name__ == "__main__":
#     import_csv_to_vector(f"../../fixtures/MattFarmerAI-TikTok-Profile-Scripts-analytics.csv")
#     print(index.describe_index_stats())