  import streamlit as st
  from bs4 import BeautifulSoup as soup
  import requests as req
  import PyPDF4
  import PyPDF4  # Changed to PyPDF4 for compatibility with PDF processing
  from io import BytesIO
  import os
  import re
  @@ -18,87 +17,142 @@
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
            response = req.get(f"{pure_url}{DOI}/")
            db_2 = soup(response.text, "html.parser")
            locator_date = db_2.find('span', {'class': 'cit'})
            # Check if the date span exists before trying to access its text
            if locator_date:
                date = locator_date.text.split(';')[0].strip()
            else:
                date = "Unknown"  # Use a placeholder or handle the absence as needed

            DOI_file.write(f"{DOI}\t{date}\n")
      DOI_trash = open('DOI_trash.txt', 'w')
      try:
          client = req.get(url)
          htmldata = client.text
          client.close()
          db = soup(htmldata, "html.parser")
          locator = db.findAll('a', {'class': 'docsum-title'}, href=True)
          locator_2 = re.findall(r'(?<=href="/)\w+', str(locator))
          links = [i for i in locator_2]
          clean_links = [str(pure_url + str(i.strip()) + '/') for i in links]

          for i in clean_links:
              try:
                  site_2 = ul.Request(i)
                  client_2 = ul.urlopen(i)
                  htmldata_2 = client_2.read()
                  client_2.close()
                  db_2 = soup(htmldata_2, "html.parser")
                  locator_date = db_2.findAll('span', {'class': 'cit'})
                  date = str(re.findall("\d{4}", str(locator_date))[0]) if locator_date else "Unknown"
                  locator_4 = db_2.findAll('a', {'class': 'id-link'})
                  for n in locator_4:
                      responseTxt_4 = n.text.encode('UTF-8')
                      responseTxt_4 = str(responseTxt_4.strip())
                      responseTxt_4 = responseTxt_4[2:-1]
                      DOI_trash.write(responseTxt_4 + '\t' + date + '\n')
              except Exception as e:
                  print(f"Error retrieving {i}: {e}")
      except Exception as e:
          print(f"Failed to fetch data from {url}: {e}")
      finally:
          DOI_trash.close()
      return True


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
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                doi, date = parts[:2]  # Ensure we only unpack the first two values
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
            else:
                # Handle lines that don't have the expected format
                print(f"Skipping line due to unexpected format: {line}")


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
      client = req.get(url)
      htmldata = client.text
      client.close()
      db = soup(htmldata, "html.parser")
      locator = db.findAll('span', {'class': 'value'})
      limite = int(re.findall('[0-9]+', str(locator[0]))[0]) // 10 + 1
      count = 1
      Results = open('Results.txt', 'w')
      while count <= limite:
          print(f"Processing page {count}/{limite} ({np.round((count/limite)*100)}%)")
          dl_intel(url, pure_url)
          url = url + '&page=' + str(count)
          count += 1
          K = open('DOI_trash.txt', 'r')
          for lines in K.readlines():
              Results.write(lines)
          K.close()
      Results.close()


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
          db_txt = soup(htmldata, "html.parser")
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
      results = open('Searched_material.txt', 'r', encoding='utf-8')
      list_material_date = [(i.split('\t')[1].strip('\n'), i.split('\t')[2].strip('\n')) for i in results.readlines()]
      date_list = [int(i[0]) for i in list_material_date]

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


  if __name__ == "__main__":
      keywords, url = prompt_for_input()
      dir_output = 'FRANK/'  # Assuming this directory already exists or handling its creation might be necessary
      os.chdir(dir_output)
      pure_url = 'https://pubmed.ncbi.nlm.nih.gov/'

      switch_page(url, pure_url)
      print('Articles retrieved successfully, beginning sorting...')
      sci(keywords)
      print('Sorting done, preparing visual representation...')

      # Button to show publication trends
      if st.button('Show Publication Trends'):
          tendency(keywords)
          st.image('trend_bar_graph.png', caption='Publication Trends')  # Display the plot

      print('Figure is ready. Check the trend_bar_graph.png file for the bar graph.')import streamlit as st
from bs4 import BeautifulSoup as soup
import requests as req
import PyPDF4
import PyPDF4  # Changed to PyPDF4 for compatibility with PDF processing
from io import BytesIO
import os
import re
@@ -18,87 +17,142 @@
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
          response = req.get(f"{pure_url}{DOI}/")
          db_2 = soup(response.text, "html.parser")
          locator_date = db_2.find('span', {'class': 'cit'})
          # Check if the date span exists before trying to access its text
          if locator_date:
              date = locator_date.text.split(';')[0].strip()
          else:
              date = "Unknown"  # Use a placeholder or handle the absence as needed

          DOI_file.write(f"{DOI}\t{date}\n")
    DOI_trash = open('DOI_trash.txt', 'w')
    try:
        client = req.get(url)
        htmldata = client.text
        client.close()
        db = soup(htmldata, "html.parser")
        locator = db.findAll('a', {'class': 'docsum-title'}, href=True)
        locator_2 = re.findall(r'(?<=href="/)\w+', str(locator))
        links = [i for i in locator_2]
        clean_links = [str(pure_url + str(i.strip()) + '/') for i in links]

        for i in clean_links:
            try:
                site_2 = ul.Request(i)
                client_2 = ul.urlopen(i)
                htmldata_2 = client_2.read()
                client_2.close()
                db_2 = soup(htmldata_2, "html.parser")
                locator_date = db_2.findAll('span', {'class': 'cit'})
                date = str(re.findall("\d{4}", str(locator_date))[0]) if locator_date else "Unknown"
                locator_4 = db_2.findAll('a', {'class': 'id-link'})
                for n in locator_4:
                    responseTxt_4 = n.text.encode('UTF-8')
                    responseTxt_4 = str(responseTxt_4.strip())
                    responseTxt_4 = responseTxt_4[2:-1]
                    DOI_trash.write(responseTxt_4 + '\t' + date + '\n')
            except Exception as e:
                print(f"Error retrieving {i}: {e}")
    except Exception as e:
        print(f"Failed to fetch data from {url}: {e}")
    finally:
        DOI_trash.close()
    return True


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
          parts = line.strip().split('\t')
          if len(parts) >= 2:
              doi, date = parts[:2]  # Ensure we only unpack the first two values
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
          else:
              # Handle lines that don't have the expected format
              print(f"Skipping line due to unexpected format: {line}")


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
    client = req.get(url)
    htmldata = client.text
    client.close()
    db = soup(htmldata, "html.parser")
    locator = db.findAll('span', {'class': 'value'})
    limite = int(re.findall('[0-9]+', str(locator[0]))[0]) // 10 + 1
    count = 1
    Results = open('Results.txt', 'w')
    while count <= limite:
        print(f"Processing page {count}/{limite} ({np.round((count/limite)*100)}%)")
        dl_intel(url, pure_url)
        url = url + '&page=' + str(count)
        count += 1
        K = open('DOI_trash.txt', 'r')
        for lines in K.readlines():
            Results.write(lines)
        K.close()
    Results.close()


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
        db_txt = soup(htmldata, "html.parser")
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
    results = open('Searched_material.txt', 'r', encoding='utf-8')
    list_material_date = [(i.split('\t')[1].strip('\n'), i.split('\t')[2].strip('\n')) for i in results.readlines()]
    date_list = [int(i[0]) for i in list_material_date]

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


if __name__ == "__main__":
    keywords, url = prompt_for_input()
    dir_output = 'FRANK/'  # Assuming this directory already exists or handling its creation might be necessary
    os.chdir(dir_output)
    pure_url = 'https://pubmed.ncbi.nlm.nih.gov/'

    switch_page(url, pure_url)
    print('Articles retrieved successfully, beginning sorting...')
    sci(keywords)
    print('Sorting done, preparing visual representation...')

    # Button to show publication trends
    if st.button('Show Publication Trends'):
        tendency(keywords)
        st.image('trend_bar_graph.png', caption='Publication Trends')  # Display the plot

    print('Figure is ready. Check the trend_bar_graph.png file for the bar graph.')