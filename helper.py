import streamlit as st
import collections
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
from matplotlib_venn_wordcloud import venn2_wordcloud
import requests


def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def make_v_wordcloud(all_rep_words, all_dem_words, label_list=["Republican","Democrat"]):

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

    fig, ax = plt.subplots(figsize=(10,10))

    #ax.set_title('Words People Think Describe The Other Party', fontsize=20)
    v = venn2_wordcloud([set(all_rep_words), set(all_dem_words)],
                    set_colors=['lightcoral', 'cornflowerblue'],
                    set_edgecolors=['w', 'w'],
                    ax=ax, set_labels=label_list)
                    #word_to_frequency=freq_dict )
    try:
        v.get_patch_by_id('11').set_color('purple')
        v.get_patch_by_id('11').set_alpha(0.2)
    except:
        pass
    
    return fig, [item[0] for item in counter.most_common(5)]

def make_barplot(data):
    fig, axiz1 = plt.subplots()
    sns.barplot(x="party", y="temp", data=data, ax=axiz1, palette=["lightcoral","cornflowerblue"])
    axiz1.set_ylabel('Feeling Thermometer Score')
    axiz1.set_yticks(range(0,100,5))
    axiz1.set_xlabel('')
    axiz1.set_xticklabels(labels=data["party"])
    axiz1.set(ylim=(0, 100))
    return fig
    