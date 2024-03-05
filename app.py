import streamlit as st
from bs4 import BeautifulSoup as soup
import requests as req
import PyPDF4
from io import BytesIO
import os
import re
import numpy as np
from matplotlib import pyplot as plt
import urllib.request as ul
import pandas as pd


def prompt_for_input(search_terms, technology_keywords):
    keywords = search_terms.split() + technology_keywords.split()
    return keywords, f"https://pubmed.ncbi.nlm.nih.gov/?term={'+'.join(search_terms.split())}&filter=simsearch2.ffrft"

def dl_intel(url, pure_url):
    DOI_trash = open('DOI_trash.txt', 'w')
    client = req.get(url)
    htmldata = client.text
    client.close()
    db = soup(htmldata, "html.parser")
    locator = db.findAll('a', {'class':'docsum-title'}, href=True)  
    locator_2 = re.findall(r'(?<=href="/)\w+', str(locator))
    links = [i for i in locator_2]
    clean_links = [str(pure_url + str(i.strip()) + '/') for i in links]

    for i in clean_links:        
        site_2 = ul.Request(i)
        client_2 = ul.urlopen(i)
        htmldata_2 = client_2.read()
        client_2.close()
        db_2 = soup(htmldata_2, "html.parser")
        locator_date = db_2.findAll('span', {'class':'cit'})
        try:
            date = str(re.findall("\d{4}", str(locator_date))[0])
        except:
            continue
        locator_4 = db_2.findAll('a', {'class':'id-link'})
        for n in locator_4:
            responseTxt_4 = n.text.encode('UTF-8')
        responseTxt_4 = str(responseTxt_4.strip())
        responseTxt_4 = responseTxt_4[2:-1]
        DOI_trash.write(responseTxt_4 + '\t' + date + '\n')

    DOI_trash.close()
    return True

def switch_page(url, pure_url):
    client = req.get(url)
    htmldata = client.text
    client.close()
    db = soup(htmldata, "html.parser")
    locator = db.findAll('span', {'class':'value'})  
    limite = int(re.findall('[0-9]+', str(locator[0]))[0])//10 + 1
    count = 1
    Results = open('Results.txt', 'w')
    while count <= limite:
        print(dl_intel(url, pure_url), f'Progression : {np.round((count/limite)*100)}%')
        url = url + '&page=' + str(count)
        count += 1
        K = open('DOI_trash.txt', 'r')
        for lines in K.readlines():
            Results.write(lines)
        K.close()
    Results.close()


def sci(keywords):    
  F = open('Results.txt', 'r', encoding='utf-8')
  articles_data = []  # Initialize an empty list to store article data
  count_bad_links = 0
  signal = 1
  for count, line in enumerate(F):
      pass
  limite = count + 1
  F.seek(0)  # Reset file pointer to the beginning

  for i in F.readlines(): 
      i = i.strip('\n').split('\t')
      print(f'article n° {str(signal)}\tloading : {np.round((signal/limite)*100)}%')
      signal += 1
      link = 'https://doi.org/' + i[0]
      date = i[1]
      try:
          retrieved_data = req.get(link)
          my_raw_data = retrieved_data.content
      except Exception:
          count_bad_links += 1
          continue

      output, dico_keywords = process_article(my_raw_data, keywords)
      max_keyword = str(max(dico_keywords, key=dico_keywords.get))
      articles_data.append({'DOI': link, 'Publication Date': date, 'Top Keyword': max_keyword})

  F.close()

  # Convert articles_data list to DataFrame
  df_articles = pd.DataFrame(articles_data)
  # Display the DataFrame in Streamlit
  st.dataframe(df_articles)

  print_results(dico_keywords, count_bad_links)


def process_article(raw_data, keywords):
    output = ''
    if b'%PDF' in raw_data:
        data = BytesIO(raw_data)
        try:
            read_pdf = PyPDF4.PdfReader(data)
            for page in range(len(read_pdf.pages)):
                txt = read_pdf.pages[page].extract_text()
                txt = txt.encode('UTF-8', errors='ignore')
                output += str(txt.strip())
        except Exception:
            pass
    else:
        db_txt = soup(raw_data, "html.parser")
        txt = db_txt.find_all(string=True)
        blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'footer', 'style']
        for t in txt:
            if t.parent.name not in blacklist:
                output += '{}'.format(t)
        output = re.sub("\n|\r|\rn", '', output)
        output = output[output.find('Abstract'):]
        output = str(output[:output.find('References')]).lower()
    dico_keywords = {keyword: output.count(keyword.lower()) for keyword in keywords}
    return output, dico_keywords

def print_results(dico_keywords, count_bad_links):
    for key, res in dico_keywords.items():
        print(key, res)
    print(f'impossible links to retrieve : {count_bad_links}')

def tendency(keywords):
    results = open('Searched_material.txt', 'r', encoding='utf-8')
    list_material_date = [(i.split('\t')[1].strip('\n'), i.split('\t')[2].strip('\n')) for i in results.readlines()]
    date_list = [int(i[0]) for i in list_material_date]
    date_range = (min(date_list), max(date_list))
    dates = np.arange(date_range[0], date_range[1] + 1)
    count_dates = {keyword: [0] * len(dates) for keyword in keywords}

    for date, keyword in list_material_date:
        if keyword in count_dates:
            index = int(date) - date_range[0]
            count_dates[keyword][index] += 1

    fig, ax = plt.subplots()
    for keyword, counts in count_dates.items():
        ax.bar(dates, counts, label=keyword)

    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Publications')
    ax.set_title('Publication Trends')
    ax.legend()
    plt.savefig('trend_bar_graph.png')
    results.close()

def main():
    st.title("PubMed Article Analysis Tool")

    # Get user input
    search_terms = st.text_input("Enter your search keywords (e.g., prokaryote sequencing):")
    technology_keywords = st.text_input("Enter technology keywords (e.g., Illumina Nanopore):")

    if search_terms and technology_keywords:
        keywords, url = prompt_for_input(search_terms, technology_keywords)

        # Create a directory for output
        dir_output = 'FRANK/'
        os.makedirs(dir_output, exist_ok=True)
        os.chdir(dir_output)

        pure_url = 'https://pubmed.ncbi.nlm.nih.gov/'
        switch_page(url, pure_url)
        st.success("Articles retrieved successfully, beginning sorting...")
        sci(keywords)
        st.success("Sorting done, preparing visual representation...")
        tendency(keywords)
        st.success("Figure is ready. Check the trend_bar_graph.png file for the bar graph.")

        # Display the image
        st.image("trend_bar_graph.png")

if __name__ == "__main__":
    main()