
# CS429 - IR Project Report 

#### Name: Vrushabh Shet
#### CWID: A20560742


## Web Based Search Engine

This project is a modular web-based search engine consisting of three main components:
 - **Crawler**: Scrapy-based spider for collecting quotes from azquotes.com.
 - **Indexer**: Python script using Scikit-Learn to build a TF-IDF inverted index and store results in JSON and pickle formats.
 - **Processor**: Flask web app for querying the index, supporting free-text, tag, and Boolean search.


## Abstract

This project implements a modular search engine pipeline:
1. **Crawler**: Uses Scrapy to download quotes from azquotes.com, saving results in HTML format.
2. **Indexer**: Processes HTML, extracts quotes, authors, and tags, builds a TF-IDF matrix, and creates an inverted index (JSON/pickle).
3. **Processor**: Flask app that loads the index and supports free-text, tag-based, and Boolean search, returning top-k ranked results with author, text, and tags.

#### - Summary:

A Crawler, Indexer, and  Processor are the three primary parts of the project that need to be developed. After initializing with a starting URL , the crawler retrieves web pages up to predetermined maximum pages and depth restrictions. Using TF-IDF representation and cosine similarity score, the Indexer creates an inverted index in pickle format. Top-ranked results are returned by the Processor based on the indexed material, which also handles free text queries in JSON format and carries out query validation and error-checking.

#### - Objectives:

   - Create a web crawler using Scrapy to download documents in HTML format.
  - Use TF-IDF representation to create an inverted index by implementing an indexer based on Scikit-Learn.
  - To rank documents during search indexing, apply cosine similarity score.
  - Build a Flask-based  processor that can process free-text queries and provide results that are ranked highly.
  - To improve the accuracy of query processing, make sure error-checking and query validation are in place.


#### - Next Steps

  - Enhance crawler to support more domains and robust error handling.
  - Optimize indexer for larger datasets and incremental updates.
  - Expand processor to support advanced Boolean, tag, and phrase search.
  - Improve UI/UX for the Flask app.
  - Add more test cases and validation for edge scenarios.

## Overview:

#### - Solution Outline:


  - **Crawler**: Scrapy spider (`quote_spider.py`) crawls azquotes.com, extracts quotes, authors, and tags, and saves them in HTML format.
  - **Indexer**: Python script (`Indexer.py`) parses HTML, builds a TF-IDF matrix, and creates an inverted index. Results are saved in `quotes.json` and previewed in pickle format.
  - **Processor**: Flask app (`flask_processor.py`) loads the index, supports free-text, tag, and Boolean search, and returns top-k results with author, text, and tags.

#### - Relevant Literature:

The proposed solution is inspired by the existing literature on web crawlers and search engine architectures. Scrapy has been widely used in the literature for web crawling because it provides a reliable and scalable framework for online scraping operations. Using Scikit-Learn to create an inverted index is a common practice in information retrieval and search engine design.

#### - Proposed System:

  - A reliable and effective method for accessing, indexing, and querying web content will be made available to users by the suggested system. 
  - The system strives to provide precise and pertinent search results while preserving scalability and performance by utilizing cutting-edge technologies and methodologies in web crawling, indexing, and query processing. 
  - Because of its modular design, the system is easily able to accommodate new features and improvements while being flexible enough to meet changing user expectations and requirements.


## Design:


#### - System Capabilities

1. **Crawler**
  - Scrapy spider (`quote_spider.py`) crawls azquotes.com, extracts quotes, authors, and tags, and saves results in HTML.
  - Configurable for max pages and depth.

2. **Indexer**
  - Processes HTML, extracts quotes, authors, and tags.
  - Builds TF-IDF matrix and inverted index using Scikit-Learn.
  - Saves index as `quotes.json` and previews in pickle format.

3. **Processor**
  - Flask app loads the index and supports:
    - Free-text search (cosine similarity)
    - Tag-based search
    - Boolean search (AND/OR/NOT)
  - Returns top-k results with author, text, and tags.


#### - Component Interactions

 - Crawler collects quotes from azquotes.com and saves HTML.
 - Indexer parses HTML, builds TF-IDF matrix, and creates inverted index (`quotes.json`).
 - Processor loads the index, processes user queries (free-text, tag, Boolean), and returns ranked results.

#### - Integration

  - These components work together to operate the search engine as a whole. The crawler supplies the content to be indexed, the indexer creates the data structures needed for efficient retrieval , and the query processor controls user input and results presentation. 
  - With popular frameworks and libraries such as Scikit-Learn, Flask, and Scrapy, the proposed system can be constructed in a modular and extensible manner, allowing for future updates and adjustments when needed.

## Architecture:

We are going to explain the software components, interfaces, and implementation specifics of the project in the architecture section:

#### - Components of software:

 Scrapy-based Web Crawler:

 - Scrapy Spider: Responsible for fetching HTML content, traversing links, and navigating web pages.
 - URL Manager: Oversees URL queue management, setting constraints on page count, depth, and starting URL/domain.
 - HTML Downloader: Retrieves HTML content of web pages.

 Scikit-Learn based Indexer module:
 - Document Processor: Extracts and preprocesses text from HTML content for indexing.
 - Indexer: Constructs an inverted index, computes TF-IDF scores, and saves the index as a pickle file.
 - Similarity Calculator: Computes cosine similarity between search queries and indexed documents.

Flask-based Processor Module:
 - Query Parser: Handles input validation, formatting, and error checking for user queries.
 - Retriever: Retrieves top search results from the inverted index based on cosine similarity.
 - Result Formatter: Presents search results in a user-friendly JSON format.

#### - Interfaces:

Interface between Crawler and Indexer: 
 - Facilitates the transfer of downloaded web documents from the crawler to the indexer.
 - Describes the methods and data formats used to transport document data.

Interface between the Indexer and Processor: 
 - Enables the indexer to send query results and indexed data to the processor.
 - Defines the format in which query parameters should be given in order to obtain ranked result


#### - Implementation Details

**Crawler**
 - Scrapy spider (`quote_spider.py`) for azquotes.com (not goodreads.com).
 - Configurable for max pages and depth.
 - Extracts quotes, authors, and tags using CSS selectors.

**Indexer**
 - Python script (`Indexer.py`) parses HTML, extracts quotes, authors, and tags.
 - Builds TF-IDF matrix and inverted index with Scikit-Learn.
 - Saves index as `quotes.json` and previews in pickle format.

**Processor**
 - Flask app (`flask_processor.py`) loads index and supports:
   - Free-text search (cosine similarity)
   - Tag-based search
   - Boolean search (AND/OR/NOT)
 - Returns top-k results with author, text, and tags.

## Operation:

I have used the Visual Studio Code application and run the following Commands.


#### - Software Commands

**Crawler**
 - `scrapy crawl quote_spider` (from `WebCrawler/Crawler`)

**Indexer**
 - `python Indexer.py` (from `WebCrawler/Indexer`)

**Processor**
 - `python flask_processor.py` (from `WebCrawler/Processor`)

#### - Inputs:


**Inputs**

**Crawler**
 - Seed URL/Domain: `https://www.azquotes.com/top_quotes.html`
 - Max Pages: configurable in spider
 - Max Depth: configurable in spider

**Indexer**
 - HTML content downloaded by crawler: `quotes_output.html`

**Processor**
 - Loads `quotes.json` and supports queries via web UI or API (`/query` endpoint)


#### - Installation

**Crawler Setup**
 - Install Scrapy: `pip install scrapy`
 - Run spider: `scrapy crawl quote_spider` (from `WebCrawler/Crawler`)

**Indexer Setup**
 - Install Scikit-Learn: `pip install scikit-learn`
 - Run indexer: `python Indexer.py` (from `WebCrawler/Indexer`)

**Processor Setup**
 - Install Flask: `pip install Flask`
 - Run processor: `python flask_processor.py` (from `WebCrawler/Processor`)

**Integration**
 - Ensure output files from each stage are available for the next (HTML → JSON → Flask app)

## Conclusion:


 Web crawler (Scrapy based):
   - Success: Using the seed URL or website that was supplied and adhering to the max pages and max depth limitations, the crawler successfully retrieves web content in HTML format.
   - Failure: The target domain may only be partially or completely crawled by the crawler as a result of problems like network faults, URL redirection, or unavailable web pages.
   - Outputs: The HTML content of the web pages that the crawler has downloaded is sent to the Indexer component.
   - Cautions/Warnings: The crawler should be built to elegantly handle edge scenarios, with retries for unsuccessful queries, respect for robots.txt, and no overloading of the target website.

  Indexer ( Scikit-Learn based):
   - Success: Using the received HTML material, the indexer successfully creates an inverted index, computes TF-IDF scores, and saves the index in a pickle file.
   - Failure: The indexer may run into problems with document processing, text extraction, or index generation, which could result in an erroneous or insufficient index.
   - Outputs: The Query Processor component uses the pickle file format that the indexer produces as its output in the terminal itself, which is the inverted index.
   - Caveats/Cautions: The indexer should be built with memory utilization, disk space, and indexing efficiency in mind in order to properly manage large-scale indexing.

Flask-based Query Processor:
   - Success: The user requests are successfully processed by the query processor, which also verifies the input, pulls the first k results from the inverted index, and displays them in a JSON format.
   - Failure: The query processor can run into problems interpreting the query, retrieving results, or formatting the results, which would result in inaccurate or lacking responses.
   - Outputs: The query processor provides the user with a JSON format containing the top-k ranked search results.
   - Warnings and caveats: The query processor should be built with response time, error management, and scalability in mind in order to handle a large amount of user inquiries.

#### - Success Results:

 - The system efficiently crawls web documents and stores in html format in a seaparate file, indexes them using TF-IDF representation , and handles free-text queries, providing top ranked results.

#### - Outputs: 
 - Crawler: Downloaded web documents in HTML format.
 - Indexer: Printed Inverted inedx , Inverted index in pickle format in terminal itself, TF-IDF matrix shape, Query vector shape, cosine similarity shape and cosine similarity score.
 - Processor: JSON-formatted top-ranked search results based on user queries. In this Project it has printed authorname, text, tags based on the cosine similarity score for the entered query.

#### - Caveats/Cautions:

 - Web Crawling: Take care to observe terms of service and robots.txt directions, among other ethical and legal considerations, when crawling websites.
 - Indexing: To prevent noise and errors in indexing, make sure that text data has been properly preprocessed.
 - Query Processing: To efficiently handle a variety of user queries, put strong error handling and validation procedures in place.

## Data Sources:


#### Web Content:


 - The web crawling component retrieves data from azquotes.com (`https://www.azquotes.com/top_quotes.html`).
 - The Flask web application runs locally at `http://127.0.0.1:5000` and allows users to submit queries and view results from the indexed quotes.


## Test cases:


  - **Web Crawler**: Validates crawling limits (seed URL, max pages, max depth), handles robots.txt, network errors, and redirects.
  - **Indexer**: Ensures correct TF-IDF and cosine similarity calculations, accurate quote extraction, and index creation.
  - **Processor**: Validates input, supports free-text, tag, and Boolean queries, and returns top-k results in JSON format.


## Source code:


### 1. quote_spider.py

 - Scrapy spider (`quote_spider.py`) crawls azquotes.com, extracts quotes, authors, and tags using CSS selectors, and saves results in `quotes_output.html`.
 - Configurable for max pages and depth.
 - Handles pagination and duplicate avoidance.


### 2. Indexer.py

 - Python script (`Indexer.py`) parses `quotes_output.html`, extracts quotes, authors, and tags.
 - Builds TF-IDF matrix and inverted index using Scikit-Learn.
 - Saves index as `quotes.json` and previews in pickle format.
 - Supports interactive search and index preview in terminal.



### 3. flask_processor.py

 - Flask app (`flask_processor.py`) loads `quotes.json` and supports free-text, tag, and Boolean search.
 - Endpoints:
   - `/` (index page)
   - `/tags` (list available tags)
   - `/query` (POST: submit search query, returns top-k results)
 - Returns results with author, text, and tags, ranked by cosine similarity.
 - Supports Boolean queries (AND/OR/NOT) and tag filtering.


## Bibliography:



#### 1. Main Data Source and Tutorials

- **AzQuotes.com** — All quotes and data for this project were collected from [azquotes.com/top_quotes.html](https://www.azquotes.com/top_quotes.html) using a custom Scrapy spider.
- **NeuralNine.** "Crawling using Scrapy," YouTube video, NeuralNine, https://youtu.be/m_3gjHGxIJc?si=F4v2tKm7kzhbyBXN

#### 2. AI Tools Used

- ChatGPT (https://chat.openai.com/)
- GitHub Copilot (https://github.com/features/copilot)
- Gemini (https://gemini.google.com/app)
- Perplexity (https://www.perplexity.ai/)

#### 3. Flask Learning Resource

- freecodecamp.org, "Flask Course - Python web application development", YouTube video, https://youtu.be/Qr4QMBUPxWo?si=H-vWwj3BeSmJrt_a

