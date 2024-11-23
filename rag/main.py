from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_chroma import Chroma
from langchain.retrievers.multi_query import MultiQueryRetriever
from lib.scraper import Scrape


class Chat:
    def __init__(self, urls: list) -> None:
        self.model_name = "llama3.1:8b-instruct-fp16"
        self.model = ChatOllama(model = self.model_name)
        self.embedding_function=OllamaEmbeddings(model = self.model_name)

        Tool = Scrape()
        docs = Tool.scrape(urls)
        # print(docs)

        self.vectordb = Chroma.from_documents(
            documents=docs,
            embedding=self.embedding_function,
        )
        self.multi_query_llm = ChatOllama(model = "llama3.2:3b")

    def retriever(self, question: str):
        QUERY_PROMPT = PromptTemplate(
            input_variables=["question"],
            template="""You are an AI language model assistant. Your task is to generate five 
            different versions of the given user question to retrieve relevant documents from a vector 
            database. By generating multiple perspectives on the user question, your goal is to help
            the user overcome some of the limitations of the distance-based similarity search. 
            Provide these alternative questions separated by newlines.
            Original question: {question}""",
        )

        retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever=self.vectordb.as_retriever(
                search_type="mmr",
                search_kwargs={'k': 5, 'fetch_k': 20}
            ), 
            llm=self.multi_query_llm,
        )

        docs = retriever_from_llm.invoke(question)
        return docs

    def generate(self, question: str):
        context = []
        docs = self.retriever(question=question)

        print("Retrieval Successfull")

        for doc in docs:
            context.append(doc.page_content)

        context = "\n\n".join(context)

        prompt = PromptTemplate.from_template(
            """You are an expert on giving information of a website based on the context.

            - Understand the question then let's step by step.
            - Provide a clear, detailed, and descriptive information about the website ONLY based on the context.
                
            `{context}`

            Question:
            `{question}`."""
        )

        chain = prompt | self.model | StrOutputParser()

        response = chain.invoke({"context": context, "question": question})
        return response


Tool = Chat(urls=["https://www.yorku.ca/about/contact/"])
response = Tool.generate("How can I contact them?")
print(response)