'''
Streamlit app to extract links from a webpage
Created: 2021-12-29
'''
import streamlit.components.v1 as components
import streamlit as st
import requests
import re
from bs4 import BeautifulSoup
import lxml

def get_html(base_url):
    '''gets the HTML from base_url'''
    req = requests.get(base_url)
    return req.text if (req.status_code == 200) else ''


def get_links(html_page):
    '''extracts all the links and sub-directories from html
    this extracts all hrefs in a tags
    '''
    # "lxml" supposed to be faster than "html.parser
    soup = BeautifulSoup(html_page, "lxml")

    regex = ".|(/$)"

    links = [f"{base_url}{link.get('href')}" for link in soup.findAll(
        'a', attrs={'href': re.compile(regex)})]
    return links


def get_sub_dirs(links):
    '''filters out the sub-directories in links'''
    sub_dirs = [link for link in links if re.search(r'/$', link)]
    return sub_dirs


def get_files(links, regex=None):
    '''filters files from links, 
    can keep files based on a regular expression
    '''
    if regex is None:
        regex = r'.nc$'
    file_links = [link for link in links if re.search(regex, link)]
    return file_links


@st.cache
def main(base_url, search_subs=True, prepend_base_url=True, regex=None):
    ''' runs the main program
    given a base_url this extracts all files from base_url 
    and its sub-directories. 
    Can supply regular expression to keep on certain files
    '''
    files = []
    html_page = get_html(base_url)
    links = get_links(html_page=html_page)
    sub_dirs = get_sub_dirs(links)
    base_files = get_files(links, regex=regex)
    files = files + base_files

    if search_subs:
        for sub in sub_dirs:
            sub_files = main(sub)
            files = files + sub_files

    if prepend_base_url:
        files = [base_url + file for file in files]

    return files


# streamlit containters
# sidebar is where the controls are
# body holds output
sidebar = st.sidebar
body = st.container()

# defines a session states
# these are changed throughout the program
if "link_area" not in st.session_state or "extracted_links" not in st.session_state:
    st.session_state['link_area'] = 'placeholder text'
    st.session_state['extracted_links'] = ["placeholder text"]

# sidebar controls
with sidebar:
    st.subheader("URL to search")
    base_url = st.text_input('make sure to include  http:// or https://',
                             'https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/netcdf/')

    search_subs = st.checkbox('Search sub-directories', value=False)

    prepend_base = st.checkbox(
        'Append base URL to output', value=True)

    st.subheader('''Filter results''')
    custom_regex = st.text_input('can be a regular expression', '.nc$')

    run_program = st.button('Get links')

    st.markdown("---")

    st.subheader("Code availability")
    st.markdown("[https://github.com](https://github.com)")


# main content
with body:
    st.title("Link extractor")
    st.subheader('''Extract all the links from a webpage.''')

    if run_program:
        with st.spinner('Wait for it...'):
            st.session_state['extracted_links'] = main(
                base_url=base_url, search_subs=search_subs, prepend_base_url=prepend_base)

    # puts links in text_area by updaing st.session_state['link_area]
    if prepend_base:
        st.session_state['link_area'] = '\n'.join(
            st.session_state['extracted_links'])
    else:
        st.session_state['link_area'] = '\n'.join(
            [x.replace(base_url, '') for x in st.session_state['extracted_links']])

    # text_area with links
    extracted_linked_text = st.text_area(
        'Extracted links:',  st.session_state['link_area'], height=150)

    # button to download data
    st.download_button("Download to file",
                       extracted_linked_text,
                       file_name="file_list.txt")

    st.write("---")

    st.subheader("Run in the terminal")
    st.markdown(
        '''Save the extracted links to *file_list.txt* and run the following command.''')
    st.code('wget -i file_list.txt')
