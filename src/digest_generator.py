from langchain_ollama.llms import OllamaLLM
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from typing import List

model = OllamaLLM(model="llama3.1")
summarize_chain = load_summarize_chain(model, chain_type="map_reduce")

def generate_summary_for_cluster(documents: List[Document]) -> str:
    if not documents:
        return "No data available for summarization."
    result = summarize_chain.invoke(documents)
    return result.get("output_text", "No summary available.")

def generate_detailed_response(documents: List[Document]) -> str:
    if not documents:
        return "No data available for summarization."
    result = summarize_chain.invoke(documents)
    return result.get("output_text", "No detailed summary available.")
