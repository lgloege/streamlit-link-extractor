'''
Streamlit app to extract links from a webpage
Created: 2021-12-29
Author: L. Gloege
'''
import streamlit.components.v1 as components
import streamlit as st
from bs4 import BeautifulSoup
from itertools import chain
import asyncio
import aiohttp
import lxml
import re


async def get_html_async(base_url):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        async with client.get(base_url) as resp:
            return await resp.text() if (resp.status == 200) else ""


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


# @st.cache
async def main(base_url, search_subs=True, prepend_base_url=True, regex=None):
    files = []
    html_page = await get_html_async(base_url)
    links = get_links(html_page=html_page)
    sub_dirs = get_sub_dirs(links)
    base_files = get_files(links, regex=regex)
    files.extend(base_files)

    # gathers files from sub-directories
    coros = [main(sub) for sub in sub_dirs]
    new_files = await asyncio.gather(*coros)
    files.extend(chain(*new_files))

    if prepend_base_url:
        files = [base_url + file for file in files]

    return files


# streamlit containters
sidebar = st.sidebar
body = st.container()

# defines a session states changed throughout the program
if "link_area" not in st.session_state or "extracted_links" not in st.session_state:
    st.session_state['link_area'] = 'placeholder text'
    st.session_state['extracted_links'] = ["placeholder text"]

# sidebar controls
with sidebar:
    st.title("Link Extractor")
    st.write("An app to scrape webpage links")

    st.title("Options")
    search_subs = st.checkbox('Search sub-directories', value=False)

    prepend_base = st.checkbox('Append base URL to output', value=True)
    custom_regex = st.text_input('Filter results by regular expression', '.')

    st.markdown("---")
    st.subheader(
        "Code available on [GitHub](https://github.com/lgloege/streamlit_link_extractor)")


# main content
with body:
    st.title("Link extractor")
    base_url = st.text_input(label='Extract links from this URL ** it must start with http:// or https:// and end with / **',
                             value='https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/netcdf/')

    # starts the program
    run_program = st.button('Get links')

    # exexcuted when run_program button clicked
    if run_program:
        with st.spinner('Wait for it...'):
            st.session_state['extracted_links'] = asyncio.run(main(
                base_url=base_url, search_subs=search_subs, prepend_base_url=prepend_base))

    # prepend the base_url
    if prepend_base:
        st.session_state['link_area'] = '\n'.join(
            st.session_state['extracted_links'])
    else:
        st.session_state['link_area'] = '\n'.join(
            [x.replace(base_url, '') for x in st.session_state['extracted_links']])

    # extracted links
    extracted_linked_text = st.text_area(
        'Extracted links:',  st.session_state['link_area'], height=150)

    # save to file
    st.download_button("Save to file",
                       extracted_linked_text,
                       file_name="file_list.txt")

    # using links with wget
    st.write("---")
    st.subheader("Download Link Content")
    st.markdown(
        '''Save the extracted links to *file_list.txt* then copy the following into your terminal''')
    st.code('wget -i file_list.txt')
