lets note, this repository is created in private mode months ago. 

# Bi-lingual Medical Information Retrieval (BiMIR)


An information retrieval system using uptodate medical data that supports persian and english languages.

Project Team Members in alphabetical order:
* Mahdi Hemmatyar
* Mohammad Ali Sadraei Javaheri
* Ali Safarpoor Dehkordi
* Alireza Sahebi
* Zahra Yousefi

## Project Structure

Different sections of project are introduced in directories 00_* to 08_* .
The report is located at:
```
doc/report.pdf
```
## Abstract
Nowadays, the abundance of medical articles in various fields makes it difficult to retrieve accurate and completely reliable medical information. The UptoDate website service provides a collection of articles with entirely reliable information. But the shortcoming is its lack of support for the Persian language for retrieving medical information and articles. In this project, using the language model and Cross-Lingual Projection methods, an attempt has been made to create a system that, by entering a Persian query, closest articles and related paragraphs are retrieved from various English articles on this site.

## Results
The MRR value for English and Persian search are 0.45 and 0.14 and the first result reported by the system was equal to the correct article-paragraph pair in 98 and 22 cases of 304 queries, respectively.
| Language | EN | FA |
| :---: | :---: | :---: |
| MRR | 0.45 | 0.14 |
| First Result | 98/304 | 22/304 |
