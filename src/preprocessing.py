from langchain_core.documents import Document
from src.models import NewsItem
from typing import List
import re
import spacy

# Download english model spaCy
nlp = spacy.load("en_core_web_sm")


#Function which convert news to documents
def convert_news_to_documents(new_list: List[NewsItem]) -> List[Document]:
    documents = []

    for item in new_list:
        title = item.title.strip() if item.title else ''
        summary = item.summary.strip() if item.summary else ''
        page_content = f"{title}\n\n{summary}".strip()

        metadata = {
            "title": title,
            "url": item.link,
            "published": item.published,
            "source": item.source
        }

        doc = Document(page_content=page_content, metadata=metadata)
        documents.append(doc)

    return documents


def clean_documents(documents: List[Document]) -> List[Document]:
    new_documents = []

    for doc in documents:
        text = doc.page_content

        # Remove HTML-tags
        text = re.sub(r"<.*?>", "", text)
        # Remove links
        text = re.sub(r"http\S+|www\S+", "", text)
        text = text.strip()

        #Let's split it up by sentences (so that the model understands the context)
        spacy_doc = nlp(text)
        cleaned_sents = []
        for sent in spacy_doc.sents:
            sent_text = sent.text.strip()
            if len(sent_text.split()) > 3:
                cleaned_sents.append(sent_text)

        cleaned_text = " ".join(cleaned_sents)

        cleaned_doc = Document(page_content=cleaned_text, metadata=doc.metadata)
        new_documents.append(cleaned_doc)

    return new_documents

