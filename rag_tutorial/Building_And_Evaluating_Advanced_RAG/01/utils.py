import litellm
from trulens.providers.litellm import LiteLLM
from trulens.core import Feedback, Select
import numpy as np
from trulens.apps.llamaindex import TruLlama
import nest_asyncio
# response = completion(
#     model="ollama/llama2", 
#     api_base="http://localhost:11434"
# )

# MODIFIED: Use the modern Tru.get_context() to select the retrieved context.
nest_asyncio.apply()


ollama_provider = LiteLLM(
    model_engine="ollama/llama3.2", 
    completion_kwargs={
                        "api_base": "http://localhost:11434"
                    }
)

class RagExample:
    # Define a relevance function using LiteLLM
    def __init__(self, context):
        self.context = TruLlama.select_context(context)
        self.qa_relevance = (
            Feedback(ollama_provider.context_relevance_with_cot_reasons, name="Answer Relevance")
            .on_input_output()
        )

        self.qs_relevance = (
            Feedback(ollama_provider.context_relevance_with_cot_reasons, name = "Context Relevance")
            .on_input()
            # .on(TruLlama.select_source_nodes().node.text, alias="context")
            .on(self.context)
            # .on(Select.RecordCalls.retrieve.args.query)
            # .on(Select.RecordCalls.retrieve.rets)
            .aggregate(np.mean)
        )

        self.groundedness = (
            Feedback(
                ollama_provider.groundedness_measure_with_cot_reasons,
                name="Groundedness"
            )
            # .on(
            #     TruLlama.select_source_nodes()
            #     .node
            #     .text
            # )
            # .on(Select.RecordCalls.retrieve.rets.collect())
            .on(self.context.collect())
            .on_output()
            .aggregate(np.mean)
        )
        self.feedbacks = [self.qa_relevance, self.qs_relevance, self.groundedness]


    def get_trulens_recorder(self, query_engine, app_id):
        context = TruLlama.select_context(query_engine)
        tru_recorder = TruLlama(
            query_engine,
            app_name=app_id,
            app_version="base",
            app_id=app_id,
            feedbacks=self.feedbacks
        )

        return tru_recorder

    def get_prebuilt_trulens_recorder(self, query_engine, app_id):
        tru_recorder = TruLlama(
            query_engine,
            app_name=app_id,
            app_version="pre_base",
            app_id=app_id,
            feedbacks=self.feedbacks
            )
        return tru_recorder



from llama_index.core import ServiceContext, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.indices.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.indices.postprocessor import SentenceTransformerRerank
from llama_index.core import load_index_from_storage
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
import os
from llama_index.vector_stores.postgres import PGVectorStore
class SentenceWindowRetrieval:
    def __init__(self):
        Settings.embed_model = OllamaEmbedding(
            model_name="bge-m3",
            base_url="http://localhost:11434",
            ollama_additional_kwargs={"mirostat": 0},
        )
        Settings.llm = Ollama(model='llama3.2', base_url='http://localhost:11434',temperature=0.1, request_timeout=300.0)
        # create the sentence window node parser w/ default settings
        Settings.node_parser = SentenceWindowNodeParser.from_defaults(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )
        self.vector_store = PGVectorStore.from_params(
            database="llama_vector",
            host="localhost",
            password="123456",
            port='5433',
            user="admin",
            table_name="llama_vector_sentence_window_retrieval",
            embed_dim=1024
        )
    def build_sentence_window_index(
        self, documents, save_dir="sentence_index"
    ):
        if not os.path.exists(save_dir):
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            sentence_index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context, show_progress=True
            )
            sentence_index.storage_context.persist(persist_dir=save_dir)
        else:
            sentence_index = load_index_from_storage(
                StorageContext.from_defaults(persist_dir=save_dir)
            )
        return sentence_index


    def get_sentence_window_query_engine(
        self,
        sentence_index,
        similarity_top_k=6,
        rerank_top_n=2,
    ):
        # define postprocessors
        postproc = MetadataReplacementPostProcessor(target_metadata_key="window")
        rerank = SentenceTransformerRerank(
            top_n=rerank_top_n, model="BAAI/bge-reranker-base"
        )

        sentence_window_engine = sentence_index.as_query_engine(
            similarity_top_k=similarity_top_k, node_postprocessors=[postproc, rerank]
        )
        return sentence_window_engine


from llama_index.core.node_parser import HierarchicalNodeParser

from llama_index.core.node_parser import get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.indices.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine

class AutoMergingRetrieval:
    def __init__(self):
        Settings.embed_model = OllamaEmbedding(
            model_name="bge-m3",
            base_url="http://localhost:11434",
            ollama_additional_kwargs={"mirostat": 0},
        )
        Settings.llm = Ollama(model='llama3.2', base_url='http://localhost:11434',temperature=0.1, request_timeout=300.0)
        # create the sentence window node parser w/ default settings
        Settings.node_parser = SentenceWindowNodeParser.from_defaults(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )
        self.vector_store = PGVectorStore.from_params(
            database="llama_vector",
            host="localhost",
            password="123456",
            port='5433',
            user="admin",
            table_name="llama_vector_auto_merging_retrieval",
            embed_dim=1024
        )
    def build_automerging_index(
        self,
        documents,
        save_dir="merging_index",
        chunk_sizes=None,
    ):
        chunk_sizes = chunk_sizes or [2048, 512, 128]
        node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=chunk_sizes)
        nodes = node_parser.get_nodes_from_documents(documents)
        leaf_nodes = get_leaf_nodes(nodes)
        storage_context = StorageContext.from_defaults()
        storage_context.docstore.add_documents(nodes)

        if not os.path.exists(save_dir):
            automerging_index = VectorStoreIndex(
                leaf_nodes, storage_context=storage_context
            )
            automerging_index.storage_context.persist(persist_dir=save_dir)
        else:
            automerging_index = load_index_from_storage(
                StorageContext.from_defaults(persist_dir=save_dir),
            )
        return automerging_index


    def get_automerging_query_engine(
        self,
        automerging_index,
        similarity_top_k=12,
        rerank_top_n=2,
    ):
        base_retriever = automerging_index.as_retriever(similarity_top_k=similarity_top_k)
        retriever = AutoMergingRetriever(
            base_retriever, automerging_index.storage_context, verbose=True
        )
        rerank = SentenceTransformerRerank(
            top_n=rerank_top_n, model="BAAI/bge-reranker-base"
        )
        auto_merging_engine = RetrieverQueryEngine.from_args(
            retriever, node_postprocessors=[rerank]
        )
        return auto_merging_engine
