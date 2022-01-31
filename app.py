'''
Streamlit app to extract links from a webpage
Created: 2021-12-29
Author: L. Gloege
'''
import streamlit as st
import fast_link_extractor as fle

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

    prepend_base = st.checkbox('Append base URL to output', value=False)
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
            st.session_state['extracted_links'] = fle.link_extractor(
                base_url=base_url,
                search_subs=search_subs,
                prepend_base_url=False,
                regex=custom_regex)

    # prepend the base_url
    if prepend_base:
        st.session_state['link_area'] = '\n'.join(fle.prepend_with_baseurl(
            st.session_state['extracted_links'], base_url))
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
