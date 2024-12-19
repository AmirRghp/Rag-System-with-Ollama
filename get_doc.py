from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class DocumentIngestor:
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._chunks = None

    # getter and setter funcs for class
    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value: str):
        self._file_path = value

    @property
    def chunks(self):
        return self._chunks

    @chunks.setter
    def chunks(self, value):
        self._chunks = value

    def ingest(self):
        # Load PDF document
        docs = []
        for file in self._file_path:
            docs.append(PyPDFLoader(file).load_and_split())
        pages = [item for sublist in docs for item in sublist]

        # Split the pages by character length
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )
        self._chunks = text_splitter.split_documents(pages)

        return self._chunks


class VectorStoreHandler:
    def __init__(self, chunks, embedding_model="your-model", base_url="127.0.0.1:11434", persist_dir="./sql_chroma_db"):
        self._chunks = chunks
        self._embedding_model = embedding_model
        self._base_url = base_url
        self._persist_dir = persist_dir
        self._embedding = OllamaEmbeddings(model=self._embedding_model, base_url=self._base_url)
        self._vector_store = None

    # getter and setter funcs for class
    @property
    def chunks(self):
        return self._chunks

    @chunks.setter
    def chunks(self, value):
        self._chunks = value

    @property
    def vector_store(self):
        return self._vector_store

    @vector_store.setter
    def vector_store(self, value):
        self._vector_store = value

    def create_vector_store(self):
        # Create and persist vector store
        self._vector_store = Chroma.from_documents(
            documents=self._chunks,
            embedding=self._embedding,
            persist_directory=self._persist_dir
        )
        return self._vector_store
