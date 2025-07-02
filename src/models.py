from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


#create class whic have containes items
class NewsItem(BaseModel):
    title: str
    summary: str
    link: Optional[HttpUrl]
    published: Optional[datetime]
    source: Optional[str] = 'rss.app'

