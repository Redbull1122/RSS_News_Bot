from typing import List,Dict
from langchain_core.documents import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans



# 1. Функция: извлекаем тексты
def extract_texts(documents: List[Document]) -> List[str]:
    new_list = []
    for doc in documents:
            doc = doc.page_content
            new_list.append(doc)
    return new_list

# 2. Функция: векторизация
def vectorize_texts(texts: List[str]):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    return X

# 3. Функция: кластеризация векторов
def cluster_vectors(X, num_clusters: int) -> List[int]:
    kmeans = KMeans(n_clusters=num_clusters, random_state=42).fit(X)
    return kmeans.labels_.tolist()

# 4. Главная функция
def cluster_documents(documents: List[Document], num_clusters: int = 5) -> Dict[int, List[Document]]:
    texts = extract_texts(documents)
    X = vectorize_texts(texts)
    labales = cluster_vectors(X, num_clusters)
    clustered = {}
    for label, doc in zip(labales, documents):
            if label not in clustered:
                    clustered[label] = []
            clustered[label].append(doc)
    return clustered


