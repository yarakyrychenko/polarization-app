import streamlit as st
from shillelagh.backends.apsw.db import connect


def insert_user_data(conn, sheet_url):
    insert = f"""
            INSERT INTO "{sheet_url}" (id, twitter_username, party, dem_words, rep_words, dem_temp, rep_temp, username_mine)
            VALUES ("{st.session_state.id}", "{st.session_state.name}", "{st.session_state.party}", "{st.session_state.dem_words}", "{st.session_state.rep_words}", "{st.session_state.dem_temp}","{st.session_state.rep_temp}","{st.session_state.username_mine}")
            """
    conn.execute(insert)

def make_dataframe(executed_query):
    import pandas as pd
    df = pd.DataFrame(executed_query.fetchall())
    df.columns = ["id", "twitter_username", "party", "dem_words", "rep_words", "dem_temp", "rep_temp"]
    df = df.drop(["id","twitter_username"],axis=1)
    return df

def make_v_wordcloud(data):
    import collections

    all_dem_words = list(data.query("party=='Republican'").dem_words)
    all_rep_words = list(data.query("party=='Democrat'").rep_words)

    all_dem_words = ", ".join(all_dem_words)
    all_rep_words = ", ".join(all_rep_words)
    all_words = all_rep_words +", " + all_dem_words
    all_dem_words = all_dem_words.split(", ")
    all_rep_words = all_rep_words.split(", ")

    n_show = len(all_words.split(", ")) if len(all_words.split(", ")) < 100 else 100
    counter=collections.Counter([word for word in all_words.split(", ") if word != ""])
    freq_dict = {item[0]: item[1] for item in counter.most_common(n_show)}
    all_dem_words = [ word for word in all_dem_words if word in list(freq_dict.keys()) ]
    all_rep_words = [ word for word in all_rep_words if word in list(freq_dict.keys()) ]

    import matplotlib.pyplot as plt
    from matplotlib_venn_wordcloud import venn2_wordcloud

    fig, ax = plt.subplots(figsize=(15,12))

    ax.set_title('Words People Think Describe The Other Party', fontsize=20)
    v = venn2_wordcloud([set(all_rep_words), set(all_dem_words)],
                    set_colors=['red', 'blue'],
                    set_edgecolors=['w', 'w'],
                    alpha = .2,
                    ax=ax, set_labels=['Republican', 'Democrat'])
                    #word_to_frequency=freq_dict )
    # add color
    #v.get_patch_by_id('10').set_color('red')
    #v.get_patch_by_id('10').set_alpha(0.4)
    #v.get_patch_by_id('01').set_color('blue')
    #v.get_patch_by_id('01').set_alpha(0.4)
    v.get_patch_by_id('11').set_color('purple')
    v.get_patch_by_id('11').set_alpha(0.2)
    
    return fig

def make_twitter_button():
    import st.components.v1 as components
    return components.html(
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
