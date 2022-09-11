import streamlit as st
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie
from datetime import datetime
from uuid import uuid4
import seaborn as sns 
import pandas as pd
from helper import load_lottieurl, make_v_wordcloud, make_barplot


st.set_page_config(
    page_title="🇺🇸 Red and Blue 🇺🇸",
    page_icon="🇺🇸",
    layout="wide",
    menu_items={
         'About': "# See how the two parties view each other." }
)


sns.set(rc={'figure.figsize':(4,5)})
sns.set_style("whitegrid")

lottie_tweet = load_lottieurl('https://assets3.lottiefiles.com/packages/lf20_t2xm9bsw.json')
st_lottie(lottie_tweet, speed=1, height=200, key="initial")
st.session_state.one_columns_params = (.1, 3.2, .1)

row0sep1, row0col1, row0sep2 = st.columns(st.session_state.one_columns_params)
with row0sep1:
    st.markdown("")

with row0col1:
    st.markdown("<h1 style='text-align: center;'> 🇺🇸 Red and Blue 🇺🇸 </h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>  discover what the two parties think about each other </h2>", unsafe_allow_html=True)

    placeholder = st.empty()
    with placeholder.container():
        with st.expander("Consent", expanded=True):
            st.markdown("""
            By submitting the form below you agree to your data being used for research. 
            Your twitter handle will be stored in a private google sheet and will not be shared with anyone (unless extraordinary circumstances force us to share it). 
            You can ask for your data to be deleted by emailing us with an ID number you'll be issued after submitting the form. 
            """)
            agree = st.checkbox("I understand and consent.")

    if agree:
        placeholder.empty()
        with st.expander("Consent", expanded=False):
            st.markdown("""
            By submitting the form below you agree to your data being used for research. 
            Your twitter handle will be stored in a private google sheet and will not be shared with anyone (unless extraordinary circumstances force us to share it). 
            You can ask for your data to be deleted by emailing us with an app ID number you'll be issued after submitting the form. 
            """)
            st.markdown("You have consented.")
     
with row0sep2:
    st.markdown("")   

st.session_state.submitted = False
st.session_state.disable = True 
st.session_state.two_columns_params = (.1, 1.5, .2, 1.5, .1)


if agree:
    import pymongo

    client = pymongo.MongoClient(st.secrets["mongo"])
    db = client.polarization
    st.session_state.collection = db.app

    formsep1, formcol1, formsep2 = st.columns(st.session_state.one_columns_params)
    with formsep1:
        st.markdown("")

    with formcol1:
        form_place = st.empty()
        with form_place.container():
            form = st.expander("Form",expanded=True)
            form.text_input("Enter a twitter handle", key="name", placeholder="e.g. @POTUS", value="")
            st.session_state.username_mine = form.radio(
                "I confirm that",
                ('This handle belongs to me.', 'This handle belongs to someone else.')) 

            dem_words, rep_words = [], []
            form.markdown("#### Please add five words that describe Republicans best")
            for i in range(5):
                rep_words.append(form.text_input("R"+str(i+1),key = "R"+str(i+1)))
            st.session_state.rep_words = ", ".join(rep_words).lower()
            form.markdown("#### Please add five words that describe Democrats best")
            for i in range(5):
                dem_words.append(form.text_input("D"+str(i+1), key = "D"+str(i+1)))
            st.session_state.dem_words = ", ".join(dem_words).lower()

            form.markdown("#### Feeling Thermometer")
            form.markdown("""The **feeling thermometer** is a popular tool in psychology and political science that is meant to measure how a person feels towards a particular group or individual. 
                        Please rate each party using the feeling thermometer. 
                        You can give a rating between 0 (the coldest) and 100 (the warmest).
                        Ratings **above 50** degrees mean you feel positive or warm toward the group. 
                        Ratings **below 50** degrees mean you feel negative or cold toward the group. 
                        If you don't feel anything toward the group, give a rating of 50.""")

            form.slider("How do you feel about Republicans?", 
                    min_value=0, max_value=100, value=50, step=1,key="rep_temp")          
            form.slider("How do you feel about Democrats?", 
                        min_value=0, max_value=100, value=50, step=1,key="dem_temp") 
            st.session_state.party = form.radio(
                     "How do you identify?",
                    ('Independent','Republican', 'Democrat')) 
            st.session_state.disable = True if st.session_state.D5 == "" else False
 
            form.warning("Please fill out every field of the form to enable the submit button.")              
            st.session_state.submitted = form.button("Submit", disabled=st.session_state.disable)
        if  st.session_state.submitted:
            form_place.empty()

        with st.expander("Form Submitted",expanded=True):
            if st.session_state.submitted:
                st.session_state.id = datetime.now().strftime('%Y%m-%d%H-%M-') + str(uuid4())
                st.markdown(f"Thanks for submitting your answers! Your app ID is **{st.session_state.id}**. [Email me](mailto:yara@nyu.edu) with it if you want your answers deleted.") 

                user_data = {
                            "id": st.session_state.id, 
                            "twitter_username": st.session_state.name, 
                            "party": st.session_state.party, 
                            "dem_words": st.session_state.dem_words, 
                            "rep_words": st.session_state.rep_words, 
                            "dem_temp": st.session_state.dem_temp,
                            "rep_temp": st.session_state.rep_temp,
                            "username_mine": st.session_state.username_mine 
                            }

                st.session_state.collection.insert_one(user_data)        
                #st.session_state.conn = connect(":memory:", adapter_kwargs = {"gsheetsapi": {"service_account_info":  st.secrets["gcp_service_account"]}})
                #insert_user_data(st.session_state.conn, st.secrets["private_gsheets_url"])

    with formsep2:
        st.markdown("")

    if st.session_state.submitted and 'df' not in st.session_state:
        with st.spinner(text="Retrieving data..."):
            cols = ['_id', "id", "twitter_username", "party", "dem_words", "rep_words", "dem_temp", "rep_temp","username_mine"]
            list1 = []
            for row in st.session_state.collection.find():
                list1.append(list(row.values()))
            df = pd.DataFrame(list1, columns = cols)
            st.session_state.df = df.drop(['_id',"id","twitter_username","username_mine"],axis=1)

    if st.session_state.submitted and 'df' in st.session_state:    

        with st.spinner(text="Making graphs..."):
            all_dem_words = list(st.session_state.df.query("party=='Republican'").dem_words)
            all_rep_words = list(st.session_state.df.query("party=='Democrat'").rep_words)
            outgroup_cloud, most_common_out = make_v_wordcloud(all_rep_words,all_dem_words, ['Democrats\nView\nRepublicans', 'Republicans\nView\nDemocrats'])   

            all_dem_words = list(st.session_state.df.query("party=='Democrat'").dem_words)
            all_rep_words = list(st.session_state.df.query("party=='Republican'").rep_words)
            ingroup_cloud, most_common_in = make_v_wordcloud(all_rep_words,all_dem_words,['Republicans\nView\nRepublicans','Democrats\nView\nDemocrats']) 

            group_means = st.session_state.df.groupby("party").agg('mean') 
            outgroup = pd.DataFrame({'party':['Democrats\nView\nRepublicans', 'Republicans\nView\nDemocrats'], 
                                'temp': [group_means.loc['Democrat','rep_temp'], group_means.loc['Republican','dem_temp']] })
            ingroup = pd.DataFrame({'party':['Republicans\nView\nRepublicans', 'Democrats\nView\nDemocrats'], 
                                'temp': [group_means.loc['Republican','rep_temp'], group_means.loc['Democrat','dem_temp']] })
            fig1 = make_barplot(ingroup)
            fig2 = make_barplot(outgroup)

        

        st.markdown("")
        textsep1, textcol1, textsep2 = st.columns(st.session_state.one_columns_params)
        with textsep1:
            st.markdown("")
        with textcol1:
            st.markdown("""
                Many researchers find that political polarization has increased in the US over the last two decades. 
                In particular, studies consistently show that **affective polarization**, i.e., favorable feelings towards own party (the ingroup) and dislike towards the other party (the outgroup), has grown. 
                This website explores how those who identify with the Republican or Democratic parties describe and feel about the parties.
                """)  
        with textsep2:
            st.markdown("")
        
        st.markdown("")
    
        row1sep1, row1col1, row1sep2, row1col2, row1sep3 = st.columns(st.session_state.two_columns_params)
        with row1sep1:
            st.markdown("")

        with row1col1:
            st.subheader("Words about **Own** Party")
            st.markdown(f"""{str(len(st.session_state.df))} people who filled out this app describe **their** party with the words below.
                The most common words describing own party were {', '.join(most_common_in)}.""")
            st.pyplot(ingroup_cloud)
        with row1sep2:
            st.markdown("")

        with row1col2:
            st.subheader("Words about **Other** Party")
            st.markdown(f"""{str(len(st.session_state.df))} people who filled out this app describe the **other** party with the words below. 
                The most common words describing the other party were {', '.join(most_common_out)}.""")
            st.pyplot(outgroup_cloud)
        with row1sep3:
            st.markdown("")

        st.markdown("")

        row2sep1, row2col1, row2sep2, row2col2, row2sep3 = st.columns(st.session_state.two_columns_params) 
        with row2sep1:
            st.markdown("")
        with row2col1:
            st.subheader("Feelings Towards Ingroup")
            st.markdown(f"""{str(len(st.session_state.df))} people who filled out this app describe their feelings towards **their** party.
                            On average, people gave their own party a **{round(sum(ingroup.temp)/2,2)}** out of 100.""")
            st.pyplot(fig1) 

        with row2sep2:
            st.markdown("")

        with row2col2:
            st.subheader("Feelings Towards Outgroup")
            st.markdown(f"""{str(len(st.session_state.df))} people who filled out this app describe their feelings towards the **other** party. 
                            On average, people gave the other party a **{round(sum(outgroup.temp)/2,2)}** out of 100.""")
            st.pyplot(fig2)                     

        with row2sep3:
            st.markdown("")

        
        st.markdown("")
        st.markdown("***")
        st.markdown("""Thank you for going through this analysis. Please share this app with others! 
                        If you have any comments, ideas or feedback, please reach out to me on Twitter [@YaraKyrychenko](https://twitter.com/YaraKyrychenko).
                        """)
        components.html(
            """
            <a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" 
            data-text="Check out this app about the US parties 🇺🇸🔥" 
            data-url="https://share.streamlit.io/yarakyrychenko/van-bavel-app/main/app.py"
            data-show-count="false">
            data-size="Large" 
            data-hashtags="republicans,democrats,usa"
            Tweet
            </a>
            <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            """
                   )
            


        


    
                      
    

