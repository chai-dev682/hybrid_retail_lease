from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from datetime import datetime
import csv
import uuid
from dotenv import load_dotenv
import config
import time

load_dotenv()

pc = Pinecone(api_key=config.PINECONE_API_KEY)
dims = 3072
spec = ServerlessSpec(
    cloud="aws", region="us-east-1"  # us-east-1
)

# check if index already exists (it shouldn't if this is first time)
if not pc.has_index(config.PINECONE_INDEX_NAME):
    # if does not exist, create index
    pc.create_index(
        name=config.PINECONE_INDEX_NAME,
        dimension=dims,  # dimensionality of embed 3
        metric='cosine',
        spec=spec
    )
    # wait for index to be initialized
    while not pc.describe_index(config.PINECONE_INDEX_NAME).status['ready']:
        time.sleep(1)

# connect to index
index = pc.Index(config.PINECONE_INDEX_NAME)


def clean_number(value):
    return int(value.replace(',', ''))

def format_date(value):
    formatted_date = datetime.strptime(value, '%m/%d/%Y')
    return formatted_date.isoformat()  # Assuming date is already in correct format

embed_model = OpenAIEmbeddings(
    model=config.ModelType.embedding,
    openai_api_key=config.OPENAI_API_KEY
)

# embed and index all our our data!
def import_csv_to_vector(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        ind = 0

        for row in reader:
            print(ind)
            ind = ind + 1
            embedding_id = str(uuid.uuid4())
            hashtags_list= [tag.strip() for tag in row[9].split(',')]
            vector = [{
                'id': embedding_id,
                'values':embed_model.embed_documents([row[8]])[0],
                'metadata': {
                    'views': clean_number(row[0]),
                    'comments': clean_number(row[1]),
                    'shares': clean_number(row[2]),
                    'likes': clean_number(row[3]),
                    'bookmark': clean_number(row[4]),
                    'duration': clean_number(row[5]),
                    'link_to_tiktok': row[6],
                    'caption': row[7],
                    'text': row[8],
                    'hashtags': hashtags_list,
                    'cover_image_url': row[10],
                    'audio_url': row[11],
                    'date': format_date(row[12]),
                },
            }]
            index.upsert(vectors=vector)
            print("done")

    print("CSV data imported successfully into pinecone vector database.")

def format_rag_contexts(matches: list):
    contexts = []
    for x in matches:
        text = (
            f"caption: {x['metadata']['caption']}\n"
            f"transcript: {x['metadata']['text']}\n"
            f"views: {x['metadata']['views']}\n"
            f"comments: {x['metadata']['comments']}\n"
            f"shares: {x['metadata']['shares']}\n"
            f"likes: {x['metadata']['likes']}\n"
            f"bookmark: {x['metadata']['bookmark']}\n"
            f"duration: {x['metadata']['duration']}\n"
            f"date: {x['metadata']['date']}\n"
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