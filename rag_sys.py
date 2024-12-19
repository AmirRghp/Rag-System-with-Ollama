from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from get_doc import DocumentIngestor, VectorStoreHandler


class RetrievalChainBuilder:
    def __init__(self, vector_store, model="your-model"):
        self._vector_store = vector_store
        self._model = model
        self._prompt = PromptTemplate.from_template(
            """
            <s> [Instructions] You are a friendly assistant. Answer the question based only on the following context. 
            If you don't know the answer, then reply, No Context available for this question {input}. [/Instructions] </s> 
            [Instructions] Question: {input} 
            Context: {context} 
            Answer: [/Instructions]
            """
        )
        self._chain = None

    @property
    def vector_store(self):
        return self._vector_store

    @vector_store.setter
    def vector_store(self, value):
        self._vector_store = value

    @property
    def chain(self):
        return self._chain

    @chain.setter
    def chain(self, value):
        self._chain = value

    def build_chain(self):
        # Create retriever
        retriever = self._vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 3, "score_threshold": 0.5},
        )

        # Create document chain
        model = ChatOllama(model=self._model)
        document_chain = create_stuff_documents_chain(model, self._prompt)

        # Build the complete retrieval chain
        self._chain = create_retrieval_chain(retriever, document_chain)
        return self._chain


class RAGSystem:
    def __init__(self, file_path):
        self._file_path = file_path

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value: str):
        self._file_path = value

    def ingest_and_create_chain(self):
        # Ingest documents
        document_ingestor = DocumentIngestor(self._file_path)
        chunks = document_ingestor.ingest()

        # Create vector store
        vector_store_handler = VectorStoreHandler(chunks)
        vector_store = vector_store_handler.create_vector_store()

        # Build retrieval chain
        retrieval_chain_builder = RetrievalChainBuilder(vector_store)
        return retrieval_chain_builder.build_chain()

    def ask(self, query: str):
        # Get the retrieval chain
        chain = self.ingest_and_create_chain()

        # Invoke the chain
        result = chain.invoke({"input": query})
        return result
