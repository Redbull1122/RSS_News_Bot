
#News Digest Telegram Bot

A Telegram bot that helps you receive news on selected topics and generates convenient, concise, 
and detailed digests using Ollama + LangChain.

##  Project description
**News Digest Bot** :

-Collects the latest news via NewsAPI
-Cleans and processes texts using spaCy
-Clusters or selects news by keywords
-Generates concise and detailed digests via Ollama (LLM)
-Can work with Telegram commands

The bot supports two main scenarios:

 -Quick digest of one fresh news item (/digest)  
-Search and analysis by keywords (/detail <query>)

##  Functionality
-Receiving one recent news item using the command `/digest`  
-Text cleaning: removing HTML, removing links,
-Generating a brief summary via Ollama LLM  
-Search by keyword using the `/detail` command — the bot finds a suitable 
article by title or content and provides a detailed analysis  
-Division of large messages into parts for Telegram  
-MarkdownV2 screening for beautiful message formatting


