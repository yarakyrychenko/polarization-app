import streamlit as st
from shillelagh.backends.apsw.db import connect
from helper import *
from datetime import datetime
from uuid import uuid4
import seaborn as sns 
import pandas as pd

from streamlit_lottie import st_lottie
import requests

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

st.set_page_config(
    page_title="🇺🇸🔥 The US. Polarized.",
    page_icon="🔥",
    layout="wide",
    menu_items={
         'About': "# See how the two parties view each other." }
)

sns.set_style("whitegrid")
sns.set_palette("vlag")

lottie_tweet = load_lottieurl('https://assets3.lottiefiles.com/packages/lf20_t2xm9bsw.json')
st_lottie(lottie_tweet, speed=1, height=200, key="initial")

st.title("🇺🇸🔥 The US. Polarized.") 
st.subheader("""Discover what the two parties think about each other.""")

placeholder = st.empty()
with placeholder.container():
    with st.expander("Consent", expanded=True):
        st.markdown("""
           By submitting the form below you agree to your data being used for research. 
           Your twitter username will be stored in a private google sheet and will not be shared with anyone (unless extraordinary circumstances force us to share it). 
           You can ask for your data to be deleted by emailing us with an ID number you'll be issued after submitting the form. 
           """)
        agree = st.checkbox("I understand and consent.")

if agree:
    placeholder.empty()
    with st.expander("Consent", expanded=False):
        st.markdown("""
           By submitting the form below you agree to your data being used for research. 
           Your twitter username will be stored in a private google sheet and will not be shared with anyone (unless extraordinary circumstances force us to share it). 
           You can ask for your data to be deleted by emailing us with an app ID number you'll be issued after submitting the form. 
           """)
        st.markdown("You have consented.")
    

st.session_state.submitted = False
st.session_state.disable = True 

if agree:
    form_place = st.empty()
    with form_place.container():
        form = st.expander("Form",expanded=True)
        form.text_input("Enter a twitter username to begin", key="name", placeholder="e.g. POTUS", value="")
        st.session_state.username_mine = form.radio(
            "I confirm that",
            ('This username belongs to me.', 'This username is belongs to someone else.')) 

        dem_words, rep_words = [], []
        form.markdown("#### Please add five words that describe Democrats best")
        for i in range(5):
            dem_words.append(form.text_input("D"+str(i+1)))
        st.session_state.dem_words = ", ".join(dem_words).lower()
        form.markdown("#### Please add five words that describe Republicans best")
        for i in range(5):
            rep_words.append(form.text_input("R"+str(i+1),key = "R"+str(i+1)))
        st.session_state.rep_words = ", ".join(rep_words).lower()

        form.markdown("#### Feeling Thermometer")
        form.slider("How warm do you feel about Democrats (0 = coldest rating; 100 = warmest rating)?", 
                    min_value=0, max_value=100, value=50, step=1,key="dem_temp")          
        form.slider("How warm do you feel about Republicans (0 = coldest rating; 100 = warmest rating)?", 
                        min_value=0, max_value=100, value=50, step=1,key="rep_temp") 
        st.session_state.party = form.radio(
                     "How do you identify?",
                    ('Independant','Republican', 'Democrat')) 
        st.session_state.disable = True if st.session_state.R5 == "" else False
 
        form.warning("Please fill out every field of the form to enable the submit button.")              
        st.session_state.submitted = form.button("Submit", disabled=st.session_state.disable)
    if  st.session_state.submitted:
        form_place.empty()

    with st.expander("Thank you",expanded=True):
        if st.session_state.submitted:
            st.session_state.id = datetime.now().strftime('%Y%m-%d%H-%M-') + str(uuid4())
            st.success("Thanks for submitting your answers!")
            st.markdown(f"Your app ID is {st.session_state.id}. Note it down and email us if you want your answers deleted.") 
                        
            st.session_state.conn = connect(":memory:", 
                            adapter_kwargs = {
                            "gsheetsapi": { 
                            "service_account_info":  st.secrets["gcp_service_account"] 
                                    }
                                        }
                        )

            insert_user_data(st.session_state.conn, st.secrets["private_gsheets_url"])

    if st.session_state.submitted and 'df' not in st.session_state:
        with st.spinner(text="Retrieving data..."):
            sheet_url = st.secrets["private_gsheets_url"]
            query = f'SELECT * FROM "{sheet_url}"'
            st.session_state.df = make_dataframe(st.session_state.conn.execute(query))

    if st.session_state.submitted and 'df' in st.session_state:    
        col1, col2 = st.columns(2)  
        st.markdown("""Many researchers find that political polarization has increased in the US over the last two decades. 
                In particular, they find that dislike of the other party, sometimes called affective polarization, has grown a lot.""")

        with st.spinner(text="Making the wordcloud..."):
            figure = make_v_wordcloud(st.session_state.df)   
            group_means = st.session_state.df.groupby("party").agg('mean') 
            group_df = pd.DataFrame({'party':['Republican', 'Democrat', 'Republican', 'Democrat'], 
                                'towards': ['Democrat', 'Republican', 'Republican', 'Democrat'],
                                'temp': [group_means.loc['Republican','dem_temp'],group_means.loc['Democrat','rep_temp'],
                                group_means.loc['Republican','rep_temp'], group_means.loc['Democrat','dem_temp']] })
            ax = sns.barplot(x="party", y="temp", hue="towards", data=group_df)
        
        with col1:
            st.header("Outgroup Animosity: Describing the **other** party.")
            st.pyplot(figure)
            st.markdown(f"""{str(len(st.session_state.df))} people who filled out this app describe the **other** with the words above. 
                            Do the words seem negative or positive?""")

        with col2:
            st.header("Feeling Thermometer")
            st.pyplot(ax)
            st.markdown(f"""{str(len(st.session_state.df))} people who filled out this app describe their feelings towards the each party. 
                        Does it seem like we prefer our own party and feel cold towards the other party?""") 


        import st.components.v1 as components
        components.html(
            """
            <a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" 
            data-text="Check out this app about the American politics 🇺🇸" 
            data-url="https://share.streamlit.io/yarakyrychenko/van-bavel-app/main/app.py"
            data-show-count="false">
            data-size="Large" 
            data-hashtags="polarization,usa"
            Tweet
            </a>
            <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            """
                   )



    
                      
    

