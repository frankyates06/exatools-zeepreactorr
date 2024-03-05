# Import necessary libraries
import streamlit as st
from bs4 import BeautifulSoup as soup
import requests as req
import PyPDF4
from io import BytesIO
import os
import re
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import urllib.request as ul

# Streamlit app title
st.title('PubMed Article Analysis Tool')

# Sidebar for user input
st.sidebar.header('User Input Parameters')
search_terms = st.sidebar.text_input('Search Keywords', 'prokaryote sequencing')
technology_keywords = st.sidebar.text_input('Technology Keywords', 'Illumina Nanopore')
def dl_intel(url, pure_url):
  DOI_trash = 'DOI_trash.txt'
  with open(DOI_trash, 'w') as DOI_file:
      client = req.get(url)
      htmldata = client.text
      db = soup(htmldata, "html.parser")
      locator = db.findAll('a', {'class': 'docsum-title'}, href=True)
      for link in locator:
          DOI = link['href'].split('/')[-1]
          response = req.get(f"https://pubmed.ncbi.nlm.nih.gov/{DOI}/")
          db_2 = soup(response.text, "html.parser")
          date = db_2.find('span', {'class': 'cit'}).text.split(';')[0].strip()
          DOI_file.write(f"{DOI}\t{date}\n")

def switch_page(url, pure_url):
  # Limit to a certain number of pages for the demo
  limite = 1  # Use a small limit for demonstration purposes
  Results = 'Results.txt'
  with open(Results, 'w') as res_file:
      for count in range(1, limite + 1):
          print(f"Processing page {count}...")
          dl_intel(url, pure_url)
          with open('DOI_trash.txt', 'r') as K:
              for lines in K:
                  res_file.write(lines)

def sci(keywords):
  Results = 'Results.txt'
  Searched_material = 'Searched_material.txt'
  with open(Results, 'r', encoding='utf-8') as F, open(Searched_material, 'w', encoding='utf-8') as SM:
      for line in F:
          doi, date = line.strip().split('\t')
          link = f'https://doi.org/{doi}'
          try:
              retrieved_data = req.get(link, timeout=10)
              my_raw_data = retrieved_data.content
              if b'%PDF' in my_raw_data:
                  SM.write(f"{link}\t{date}\tPDF\n")
              else:
                  SM.write(f"{link}\t{date}\tHTML\n")
          except Exception as e:
              print(f"Failed to retrieve {link}: {e}")

def tendency():
  Searched_material = 'Searched_material.txt'
  with open(Searched_material, 'r', encoding='utf-8') as SM:
      dates = [line.split('\t')[1] for line in SM]
      years = [date.split('-')[0] for date in dates if '-' in date]
      year_count = {year: years.count(year) for year in set(years)}
      years_sorted = sorted(year_count.keys())
      counts_sorted = [year_count[year] for year in years_sorted]

      plt.figure(figsize=(10, 6))
      plt.bar(years_sorted, counts_sorted, color='skyblue')
      plt.xlabel('Year')
      plt.ylabel('Number of Articles')
      plt.title('Number of Articles Retrieved Per Year')
      plt.xticks(rotation=45)
      plt.tight_layout()
      return plt
keywords = search_terms.split() + technology_keywords.split()
url = f"https://pubmed.ncbi.nlm.nih.gov/?term={'+'.join(search_terms.split())}&filter=simsearch2.ffrft"

if st.button('Retrieve and Analyze Articles'):
    with st.spinner('Fetching articles from PubMed...'):
        switch_page(url, 'https://pubmed.ncbi.nlm.nih.gov/')
        sci(keywords)
    st.success('Articles retrieved and sorted. Click on "Show Publication Trends" to view the analysis.')

if st.button('Show Publication Trends'):
    fig = tendency()
    st.pyplot(fig)
