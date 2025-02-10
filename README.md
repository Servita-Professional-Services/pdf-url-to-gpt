# pdf-url-to-gpt
GPTs are awful at returning page numbers and doc titles when its given raw docs. This converts a folder of files into a single json file which the GPT can read well. This will enable it to coherently tell you what page of a document the source information was on and the document title and url.

This repository contains a Python script that processes a folder of PDF files and (optionally) web URLs to generate a structured `citations.json` file. This JSON file consolidates citation data including document titles, page numbers, text snippets, and in-line clickable SharePoint URL links. The script also integrates a CSV file mapping PDF filenames to their respective web urls if you have them stored in internal tools like SharePoint.

## Features

- **PDF Processing:**  
  Extracts text and metadata from each page of PDF files in a specified folder.

- **Web URL Processing (Optional):**  
  Extracts visible text and page titles from provided web URLs.

- **SharePoint Mapping Integration:**  
  Loads a CSV file containing document names, titles, and SharePoint URL links. If a PDF’s filename matches an entry in the CSV, the script adds the associated in-line URL to the citation data.

- **JSON Output:**  
  Consolidates all citation data into a single `citations.json` file for easy integration with downstream tools (e.g., GPT training).

- **Debugging Information:**  
  Provides debug messages to assist with verifying CSV mappings and file processing.

## Suggested usage

- Dump all required PDF files into the src/PDFs folder
- Optional: Update the CSV file to include web links to PDFs if hosted internally (this allows the GPT to provide a hyperlink to the content in its response)
- Optional: Update the script to point at any specific weblinks you would like to include in the dataset
- Run!

## Prerequisites

- **Python Version:** Python 3.7 or higher

- **Required Packages:**  
  - `PyPDF2`
  - `requests`
  - `beautifulsoup4`

Install the required packages using pip:

```bash
pip install PyPDF2 requests beautifulsoup4
python pdf-to-gpt.py

