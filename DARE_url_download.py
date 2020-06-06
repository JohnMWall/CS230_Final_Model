import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import sys
import re

ROOT_URL = 'https://search.library.wisc.edu/search/digital?filter%5Bfacets%5D%5Bcollections_facet~DARE+Fieldwork+Recordings%5D=yes&'
EX_ROOT_URL = 'https://search.library.wisc.edu'
WAIT = 1.2
DEBUG = True

def get_htmls(urls):
    '''
    Retrieves html in text form from ROOT_URL
    :param urls (list): List of urls from which to retrieve html
    :return (list): list of HTML strings
    '''
    htmls = []
    for url in urls:
        if DEBUG:
            print('downloading from {}'.format(url))
        htmls.append(requests.get(url).text)
        time.sleep(WAIT)

    return(htmls)


def build_search_urls(numPages):
    '''
    creates url from ROOT_URL and page number
    :return (list): List of urls for the examples
    '''
    all_search_pages = []
    #all_search_pages.append(ROOT_URL+'view=thumb')
    if numPages > 1:
        for pageNum in range(41,numPages+1):
        # for pageNum in range(numPages,numPages+1):
            all_search_pages.append(ROOT_URL+'page='+str(pageNum)+'&view=thumb')
    return(all_search_pages)

def parse_a(a_tag):
    '''
    Extracts href property from HTML <a> tag string
    :param a_tag (str): HTML string
    :return (str): string of link
    '''
    text = EX_ROOT_URL + a_tag
    return(text)

def get_bio(hrefs):
    '''
    Retrieves HTML from list of hrefs and returns bio information
    :param hrefs (list): list of hrefs
    :return (DataFrame): Pandas DataFrame with bio information
    '''

    htmls = get_htmls(hrefs)
    bss = [BeautifulSoup(html,'html.parser') for html in htmls]
    bio_row = []
    for bs in bss:
        rows = []
        headerParsed = parse_header(bs.title.string)
        rows.append(headerParsed[0])
        rows.append(headerParsed[1])
        numID = rows[1]
        for info in bs.find_all('li'):
            if info.text.startswith(str(numID)):
                tempInfo = info.text
                verSplit = re.split(': |; ',tempInfo)
                if len(verSplit) < 5:
                    continue
                ageSplit = re.split(' ',verSplit[4])

                if len(ageSplit) < 2 or len(verSplit) < 9:
                    continue

                rows.append(verSplit[1])
                rows.append(verSplit[2])
                
                rows.append(ageSplit[0])
                rows.append(ageSplit[1])
                rows.append(verSplit[6])
                rows.append(verSplit[8])
                break
        bio_row.append(rows)
    return(pd.DataFrame(bio_row))

def parse_header(head):


    cols = []
    headerSplit = re.split(': |; ', head)
    location = headerSplit[1]
    cols.append(re.split(', ', location))

    tempID = headerSplit[2]
    ID = re.split(' ', tempID)[2]
    cols.append(ID)
    return cols

def create_dataframe(numPages):
    '''

    :param languages (str): language from which you want to get html
    :return df (DataFrame): DataFrame that contains all audio metadata from searched language
    '''
    htmls = get_htmls(build_search_urls(numPages)) #63 pages
    bss = [BeautifulSoup(html,'html.parser') for html in htmls]
    persons = []

    for bs in bss:
        for link in bs.find_all('a'):
            newLink = link.get('href')
            if newLink.startswith('/digital/'):
                persons.append(parse_a(newLink))
    #persons.append('https://search.library.wisc.edu/digital/AOE3YTBLR4LTUB8F')

    df = pd.DataFrame(persons, columns=['href'])

    bio_row = get_bio(df['href'])

    if DEBUG:
        print('loading finished')

    #print(bio_row)

    df['ID'] = bio_row.iloc[:,1]
    df['location'] = bio_row.iloc[:,0]
    df['ethnicity'] = bio_row.iloc[:,2]
    df['sex'] = bio_row.iloc[:,3]
    df['age'] = bio_row.iloc[:,4]
    df['age group'] = bio_row.iloc[:,5]
    df['education'] = bio_row.iloc[:,6]
    df['community type'] = bio_row.iloc[:,7]

    return(df)

if __name__ == '__main__':
    '''
    console command example:
    '''

    df = None

    # Set destination file
    destination_file = sys.argv[1]

    # Check if destination file exists, else create a new one
    try:
        df = pd.read_csv(destination_file)
        df = df.append(create_dataframe(63),ignore_index=True) #63 pages

    except:
        df = create_dataframe(63) #63 pages

    #df.drop_duplicates(subset='language_num',inplace=True)

    df.to_csv(destination_file,index=False)