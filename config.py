from enum import Enum
from glob import glob
from logging import getLogger
from logging.config import fileConfig
from os.path import join, isfile
from os import environ
from dotenv import load_dotenv
import json
import os

load_dotenv()

PROJECT_ROOT = "./"
LOG_INI = join(PROJECT_ROOT, 'log.ini')
FIXTURES = join(PROJECT_ROOT, 'fixtures')

# pinecone
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def load_env():
    load_dotenv(join(PROJECT_ROOT, ".env"))


class PromptTemplate(Enum):
    QUERY_TRANSFER = "query_transformation.txt"
    SQL_VECTOR = "sql_vector.txt"
    GEN_SQL_QUERY = "gen_sql_query.txt"
    GEN_QUERY = "gen_query.txt"
    ANSWER = "answer.txt"


class Fixtures(Enum):
    EXAMPLE_CONVERSATION = "examples.txt"


class FunctionTemplate(Enum):
    SQL_VECTOR = "sql_vector.json"


class ModelType(str, Enum):
    gpt4o = 'gpt-4o'
    gpt4o_mini = 'gpt-4o-mini'
    embedding = "text-embedding-3-large"


def get_prompt_template(prompt_template: PromptTemplate):
    with open(join(PROJECT_ROOT, "prompt_templates", prompt_template.value), "rt") as f:
        return f.read()


def get_function_template(function_template: FunctionTemplate):
    with open(join(PROJECT_ROOT, "function_templates", function_template.value), "r") as f:
        return json.loads(f.read())


def get_fixture(fixture: Fixtures):
    with open(join(PROJECT_ROOT, "fixtures", fixture.value), "rt") as f:
        return f.read()


def configure_logging(get_logger=False):
    global logging_configured
    if not logging_configured:
        fileConfig(LOG_INI)
        logging_configured = True
    if get_logger:
        logger = getLogger('freedo')
        return logger
