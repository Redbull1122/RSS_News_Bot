from langchain_ollama.llms import OllamaLLM
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from typing import List

# Initialize Ollama LLM with the specified model
model = OllamaLLM(model="llama3.1")
summarize_chain = load_summarize_chain(model, chain_type="map_reduce")

#Generate a concise summary for a cluster of documents.
# If no documents are provided, return a default message.
def generate_summary_for_cluster(documents: List[Document]) -> str:
    if not documents:
        return "No data available for summarization."
    # Invoke the summarization chain on the list of documents
    result = summarize_chain.invoke(documents)
    # Return the summary text or a default message if not available
    return result.get("output_text", "No summary available.")

#Generate a detailed summary for a list of documents.
#If no documents are provided, return a default message.
def generate_detailed_response(documents: List[Document]) -> str:
    if not documents:
        return "No data available for summarization."
    result = summarize_chain.invoke(documents)
    # Return the detailed summary text or a default message if not available
    return result.get("output_text", "No detailed summary available.")
