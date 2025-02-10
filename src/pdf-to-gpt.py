import os
import re
import json
import csv
import PyPDF2
import requests
from bs4 import BeautifulSoup

# -------------------------------
# Load SharePoint Links Mapping from CSV
# -------------------------------

def load_sharepoint_links(csv_path):
    """
    Loads SharePoint links from a CSV file.
    The CSV must have columns: "Document Name", "Title", "Web Link"
    Returns a dictionary mapping lower-case document names to a dict with title and web_link.
    """
    mapping = {}
    try:
        # Use utf-8-sig to handle possible BOM and newline=''
        with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            # Debug: print the detected headers
            print("[DEBUG] CSV Headers:", reader.fieldnames)
            for row in reader:
                # Normalize row keys by stripping whitespace from keys
                row = {key.strip(): value for key, value in row.items() if key is not None}
                # Debug: print the current row keys
                # print("[DEBUG] CSV Row:", row)
                
                # Use .get() to avoid KeyError and strip extra spaces
                doc_name_raw = row.get("Document Name")
                if not doc_name_raw:
                    print("[DEBUG] 'Document Name' key not found in row:", row)
                    continue
                doc_name = doc_name_raw.strip().lower()
                title = row.get("Title", "").strip()
                web_link = row.get("Web Link", "").strip()
                mapping[doc_name] = {
                    "title": title,
                    "web_link": web_link
                }
    except Exception as e:
        print(f"Error loading SharePoint links from '{csv_path}': {e}")
    return mapping
# -------------------------------
# Helper Function: Process PDFs
# -------------------------------

def extract_pdf_info(pdf_path, sharepoint_links):
    """
    Extracts citation information from a PDF file.
    For each page in the PDF, returns a dictionary with:
      - source_type: 'pdf'
      - document_title: from SharePoint mapping (if available) or PDF metadata/filename
      - page_number: page number (1-indexed)
      - text: content of the page
      - web_link: the SharePoint URL if available (else not included)
    """
    import os, re, PyPDF2
    citations = []
    file_name = os.path.basename(pdf_path).strip()
    
    # Normalize the file name to lower case and remove extra spaces
    file_key = file_name.lower()
    sp_data = sharepoint_links.get(file_key)
    
    if not sp_data:
        # Print a debug message if no SharePoint entry is found for this file
        print(f"[DEBUG] No SharePoint mapping found for file: '{file_name}' (key: '{file_key}')")
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            # Retrieve document title from metadata; if missing, use the file name.
            metadata = reader.metadata
            doc_title = metadata.title if metadata and metadata.title else os.path.splitext(file_name)[0]
            # Override with SharePoint title if available.
            if sp_data:
                doc_title = sp_data.get("title", doc_title)
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                text = re.sub(r'\s+', ' ', text).strip()
                citation_entry = {
                    'source_type': 'pdf',
                    'document_title': doc_title,
                    'page_number': i + 1,  # pages are 1-indexed
                    'text': text
                }
                # Add the web_link if available from the SharePoint mapping.
                if sp_data and sp_data.get("web_link"):
                    citation_entry['web_link'] = sp_data.get("web_link")
                citations.append(citation_entry)
    except Exception as e:
        print(f"Error processing PDF '{pdf_path}': {e}")
    return citations


# -------------------------------
# Helper Function: Process Web URLs
# -------------------------------

def extract_web_info(url):
    """
    Extracts citation information from a webpage.
    Returns a dictionary with:
      - source_type: 'web'
      - document_title: from the <title> tag (or fallback to URL)
      - page_number: None (webpages do not have pages)
      - text: full visible text of the page
      - url: the original URL for traceability
    """
    citations = []
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_tag = soup.find('title')
        doc_title = title_tag.get_text().strip() if title_tag else url
        
        texts = soup.stripped_strings
        full_text = " ".join(texts)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        
        citations.append({
            'source_type': 'web',
            'document_title': doc_title,
            'page_number': None,
            'text': full_text,
            'url': url
        })
    except Exception as e:
        print(f"Error retrieving URL '{url}': {e}")
    return citations

# -------------------------------
# Main Routine: Generate JSON Dataset
# -------------------------------

def generate_citation_dataset(folder, urls, sharepoint_csv, output_file='citations.json'):
    """
    Processes all PDF files in the specified folder and provided web URLs.
    Uses the SharePoint CSV mapping to add in-line URL links.
    Extracts citation data and writes the combined dataset to a JSON file.
    
    Parameters:
      - folder: Folder path containing PDF files.
      - urls: List of web URLs to process.
      - sharepoint_csv: Path to the CSV file with SharePoint links.
      - output_file: Filename for the JSON output.
    """
    all_citations = []
    sharepoint_links = load_sharepoint_links(sharepoint_csv) if sharepoint_csv else {}

    # Process all PDF files in the folder
    for file in os.listdir(folder):
        if file.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder, file)
            print(f"Processing PDF: {pdf_path}")
            citations = extract_pdf_info(pdf_path, sharepoint_links)
            all_citations.extend(citations)
    
    # Process provided web URLs
    for url in urls:
        print(f"Processing URL: {url}")
        citations = extract_web_info(url)
        all_citations.extend(citations)
    
    # Write the complete citation dataset to a JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({'citations': all_citations}, f, ensure_ascii=False, indent=2)
        print(f"Successfully wrote {len(all_citations)} citations to '{output_file}'")
    except Exception as e:
        print(f"Error writing to file '{output_file}': {e}")

# -------------------------------
# Script Entry Point
# -------------------------------

if __name__ == '__main__':
    # Specify the folder containing your PDF files.
    folder_path = r"PDFs"
    
    # List of web URLs to include (if any). Add URLs as needed.
    urls = [
        #"https://transform.england.nhs.uk/",
        #"https://www.gov.uk/government/publications/" - Uncomment me to include
    ]
    
    # Path to the CSV file containing SharePoint links.
    sharepoint_csv = r"urls-for-document-references.csv"
    
    # Generate the citation dataset and output to 'citations.json'
    generate_citation_dataset(folder_path, urls, sharepoint_csv, output_file='citations.json')