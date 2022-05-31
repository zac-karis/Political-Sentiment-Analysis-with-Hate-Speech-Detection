import streamlit as st
import re

# display app header and sidebar
# use HTML code to set div
def display_app_header(main_txt, sub_txt, is_sidebar=False):
    """
    function to display major headers at user interface
    ----------
    main_txt: str -> the major text to be displayed
    sub_txt: str -> the minor text to be displayed 
    is_sidebar: bool -> check if its side panel or major panel
    """

    html_temp = f"""
    <h2 style = "color:#F74369; text_align:center; font-weight: bold;"> {main_txt} </h2>
    <p style = "color:#BB1D3F; text_align:center;"> {sub_txt} </p>
    </div>
    """
    if is_sidebar:
        st.sidebar.markdown(html_temp, unsafe_allow_html=True)
    else:
        st.markdown(html_temp, unsafe_allow_html=True)


def check_facebook_url(url):
    # confirm facebook url is valid
        url_pattern = re.compile(r'(?:(?:http|https):\/\/)?(?:www.)?facebook.com\/(?:(?:\w)*#!\/)?(?:pages\/)?(?:[?\w\-]*\/)?(?:profile.php\?id=(?=\d.*))?([\w\-]*)?')
        url_conf = url_pattern.search(url)
        return url_conf

def check_twitter_url(url):
    # confirm the url is valid
        url_pattern = re.compile(r'http(?:s)?:\/\/(?:www\.)?twitter\.com\/([a-zA-Z0-9_]+)/')
        url_conf = url_pattern.search(url)
        return url_conf