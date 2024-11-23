from langchain_ollama.chat_models import ChatOllama
from langchain.chains import create_extraction_chain
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
import pprint
from langchain_core.output_parsers import JsonOutputParser
from typing import Optional, List
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field




class Scrape:
    def __init__(self) -> None:
        self.llm = ChatOllama(model="llama3.1:70b-instruct-q4_0", temperature=0)

    def scrape(self, urls):
        loader = AsyncChromiumLoader(urls)
        docs = loader.load()
        bs_transformer = BeautifulSoupTransformer()
        docs_transformed = bs_transformer.transform_documents(
            docs, tags_to_extract=["span", "p", "li", "article", "h1", "h2", "h3", "h4"]
        )
        return docs_transformed


    def extractor(self, urls: list):
        class Information(BaseModel):
            body: str = Field(default=None, description="extracted useful information from the website")

        parser = JsonOutputParser(pydantic_object=Information)

        template = """
            You are an expert extraction algorithm.\n
            Extract all the useful content as it is from the below text which is scraped from a website.\n
            {text}

            Strictly follow the format instructions to return the response as a JSON.
            {format_instructions}
            """


        prompt = PromptTemplate(
            template = template,
            input_variables=["text"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        docs = self.scrape(urls)
        runnable = prompt | self.llm | parser
        

        for doc in docs:
            text = doc.page_content
            extracted_content = runnable.invoke({"text": "What do you know about websites?"})
            print(extracted_content)
    
# Model = Scrape()
# docs = Model.scrape(['https://www.yorku.ca/about/contact/'])
# pprint.pprint(docs)