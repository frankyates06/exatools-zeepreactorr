import streamlit as st
from bs4 import BeautifulSoup
import requests
import PyPDF4
from io import BytesIO
import os
import re
import numpy as np
from matplotlib import pyplot as plt
import urllib.request

def prompt_for_input():
    print("Welcome to the PubMed Article Analysis Tool.")
    search_terms = input("Please enter your search keywords (e.g., prokaryote sequencing): ")
    technology_keywords = input("Please enter technology keywords (e.g., Illumina Nanopore): ")
    keywords = search_terms.split() + technology_keywords.split()
    url = f"https://pubmed.ncbi.nlm.nih.gov/?term={'+'.join(search_terms.split())}&filter=simsearch2.ffrft"
    return keywords, url

def process_article(raw_data, keywords):
    output = ''
    if b'%PDF' in raw_data:
        try:
            data = BytesIO(raw_data)
            read_pdf = PyPDF4.PdfReader(data)
            for page in range(len(read_pdf.pages)):
                txt = read_pdf.pages[page].extract_text()
                txt = txt.encode('UTF-8', errors='ignore')
                output += str(txt.strip())
        except Exception:
            pass
    else:
        db_txt = BeautifulSoup(raw_data, "html.parser")
        txt = db_txt.find_all(string=True)
        blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'footer', 'style']
        for t in txt:
            if t.parent.name not in blacklist:
                output += '{} '.format(t)
        output = re.sub("\n|\r|\rn", '', output)
        output = output[output.find('Abstract'):]
        output = str(output[:output.find('References')]).lower()
    dico_keywords = {keyword: output.count(keyword.lower()) for keyword in keywords}
    return output, dico_keywords

def print_results(dico_keywords, count_bad_links):
    for key, res in dico_keywords.items():
        print(key, res)
    print(f'Failed to retrieve links: {count_bad_links}')

def tendency(keywords):
    try:
        results = open('Searched_material.txt', 'r', encoding='utf-8')
        list_material_date = [(i.split('\t')[1].strip('\n'), i.split('\t')[2].strip('\n')) for i in results.readlines()]
        date_list = [int(i[0]) for i in list_material_date]
    except FileNotFoundError:
        print("File 'Searched_material.txt' not found. Publication trends plot cannot be generated.")
        return

    # Check if there are any dates available before plotting
    if not date_list:
        print("No dates found in data. Publication trends plot cannot be generated.")
        return

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

def sci(keywords):
    try:
        with open('Results.txt', 'r', encoding='utf-8') as F:
            count_bad_links = 0
            signal = 1
            lines = F.readlines()
            limite = len(lines)

            with open('Searched_material.txt', 'w', encoding='utf-8') as Searched_material:
                for line in lines:
                    print(f'article n° {str(signal)}\tloading : {np.round((signal/limite)*100)}%')
                    signal += 1
                    line = line.strip('\n').split('\t')
                    link = 'https://doi.org/' + line[0]
                    date = line[1]

                    try:
                        retrieved_data = requests.get(link)
                        my_raw_data = retrieved_data.content
                    except Exception:
                        count_bad_links += 1
                        continue

                    output, dico_keywords = process_article(my_raw_data, keywords)
                    max_keyword = max(dico_keywords, key=dico_keywords.get)
                    Searched_material.write(f"{link}\t{date}\t{max_keyword}\n")

        print_results(dico_keywords, count_bad_links)
    except FileNotFoundError:
        print("File 'Results.txt' not found.")

if __name__ == "__main__":
    st.title('PubMed Article Analysis Tool')

    st.sidebar.header('User Input Parameters')
    keywords, url = prompt_for_input()

    dir_output = 'FRANK/'
    if not os.path.exists(dir_output):
        os.makedirs(dir_output)
    os.chdir(dir_output)

    pure_url = 'https://pubmed.ncbi.nlm.nih.gov/'

    # Fetch and process articles
    switch_page(url, pure_url)
    print('Articles retrieved successfully, beginning sorting...')
    sci(keywords)
    print('Sorting done, preparing visual representation...')

    # Button to show publication trends
    if st.button('Show Publication Trends'):
        tendency(keywords)
        st.image('trend_bar_graph.png', caption='Publication Trends')

    print('Figure is ready. Check the trend_bar_graph.png file for the bar graph.')