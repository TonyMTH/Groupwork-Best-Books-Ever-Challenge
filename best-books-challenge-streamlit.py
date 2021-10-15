import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
# import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import ast
import copy
import datetime

from streamlit_helpers import *

#import data
data_original = pd.read_csv('best-books.csv')

# Add column of min_max rating normalization
minmax_norm_ratings = min_max_normalization(data_original['avg_rating'])
data_original['minmax_norm_ratings'] = minmax_norm_ratings

# Add column of mean normalization
mean_norm_ratings = mean_normalization(data_original['avg_rating'])
data_original['mean_norm_ratings'] = mean_norm_ratings

# Add column for number of awards
data = data_original.copy()
data = data.replace({'awards': {np.nan: 0}})

d = []
for i in data.index:
    if data.loc[i, "awards"] == 0:
        d.append(0)
    else:
        d.append( len( ast.literal_eval(data.loc[i, "awards"]) ) )
data['awards_length'] = d

#set css styling
st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: 90%;
        padding-top: 5rem;
        padding-right: 5rem;
        padding-left: 5rem;
        padding-bottom: 5rem;
    }}
    img{{
    	max-width:60%;
        display: block;
        margin-left: 100px;
        margin-right: auto;
    	margin-bottom:40px;
    }}
</style>
""",
        unsafe_allow_html=True,
    )

#sidebar and headers
logo = Image.open("logo.png")
st.sidebar.image(logo, width=100)
st.sidebar.markdown("# Best Books of all Time")
st.sidebar.markdown("### Anthony Nwachukwu\n### Dan Adrian\n")



# title
st.title("A Study on the Top 5000+ Books of all Time\n\n")



# display all/some data
st.subheader("Interacting with the data")
# ,'awards_length'
disp_options = ['url','title','author','num_reviews','num_ratings','avg_rating','num_pages','original_publish_year','series','genres','awards','places','description','book_index','minmax_norm_ratings','mean_norm_ratings']
disp_options2 = ['url','title','author','avg_rating','num_pages','original_publish_year','series','genres','description']
disp_options3 = ['title','author','minmax_norm_ratings','mean_norm_ratings']

data = data.replace({'places': {np.nan: '[]'}})
# data = data.replace({'genres': {True: 'Series', False:'Non Series'}})

data = data.replace({'original_publish_year': {np.nan: 0}})
data = data.replace({'num_pages': {np.nan: 0}})
now = datetime.datetime.now()
now_year = now.year
data['original_publish_year'] = data['original_publish_year'] .apply(lambda x: int(x) if x <= now_year else 0)
data['num_pages'] = data['num_pages'] .apply(lambda x: int(x))

display_data = data[disp_options2]

select_list = st.selectbox('What detail would you like to search for?',('All','Title','Author','Original Publish Year','Series','Genres'),key='All')

if select_list == 'All':
    st.write(display_data)
else:
    select_list = '_'.join(select_list.lower().split())
    selected_option = st.selectbox('Select '+select_list.replace('_',' '), display_data[select_list].sort_values(ascending=False).unique())
    displayed_data = display_data[display_data[select_list] == selected_option]
    st.write(displayed_data)


#Analysis and Plots

# plot 1
st.subheader("Frequent Occurring Words in the Description")
display_data_description = copy.deepcopy(data)
no_words = st.slider('Number of words', 1, 100, 30)
book_option = st.selectbox('Select title', display_data_description['title'].sort_values().unique())

word_display_data_description = text_by_image(display_data_description,book_option,no_words,30)



# plot 2: Plot Authors and their mean average ratings

st.subheader("Authors with Quality Publications")

select_list_author_rating = st.selectbox('Select the plot',('Bar','Pie','Line','Horizontal Bar'),key='Pie')
charts_author_rating = {'Bar':'bar','Pie':'pie','Line':'line','Horizontal Bar':'barh'}

no_of_authors_author_rating = st.slider('Select number of authors', 1, 100, 10)
data_author_rating = data.groupby('author')['minmax_norm_ratings'].mean().sort_values(ascending=False).head(no_of_authors_author_rating)

y_label_author_rating = "Rating"
x_label_author_rating = "Author"
title_author_rating = "Select Author and Check their Ratings"

author_awards_author_rating = make_plot(data_author_rating, x_label_author_rating, y_label_author_rating,\
     title_author_rating, st, kind=charts_author_rating[select_list_author_rating])



# plot 3: Plot Authors and their total awards

st.subheader("Most Successful Authors")

select_list = st.selectbox('Select the plot',('Bar','Pie','Line','Horizontal Bar'),key='Horizontal Bar')
charts = {'Bar':'bar','Pie':'pie','Line':'line','Horizontal Bar':'barh'}

no_of_authors = st.slider('Select number of authors', 1, 100, 30)
author_awards = data.groupby('author')['awards_length'].sum().sort_values(ascending=False).head(no_of_authors)

y_label = "Total Award"
x_label = "Author"
title = "Authors with More Awards"

author_awards = make_plot(author_awards, x_label, y_label, title, st, kind=charts[select_list])



#plot 4
st.subheader("Years with Quality Publications")

select_list = st.selectbox('Select the plot',('Bar','Pie','Line','Horizontal Bar'),key='Line')
charts = {'Bar':'bar','Pie':'pie','Line':'line','Horizontal Bar':'barh'}
min_year = sorted([i for i in data.original_publish_year if i > 0])[0]

min_year = st.text_input(label= 'Min Year', value=2000)
max_year = st.text_input(label= 'Max Year', value=now_year)

year_rating = data.groupby(['original_publish_year'], as_index=False)['minmax_norm_ratings'].mean().sort_values(by='minmax_norm_ratings', ascending=False)
year_rating = year_rating.loc[(year_rating['original_publish_year'] >= int(min_year)) & (year_rating['original_publish_year'] <= int(max_year))]
year_rating.set_index('original_publish_year', inplace=True)
year_rating = year_rating['minmax_norm_ratings']

y_label = "Rating"
x_label = "Year"
title = "Publishing Year and Mean Average Ratings"

year_ratings = make_plot(year_rating, x_label, y_label, title, st, kind=charts[select_list])


# # plot 6
st.subheader("Is series more loved than non series books?")
select_list = st.selectbox('Select the plot',('Bar','Pie'),key='Bar')
charts = {'Bar':'bar','Pie':'pie'}
series_ratings = data.groupby('series')['minmax_norm_ratings'].mean().sort_values( ascending=False)
y_label = "Rating"
x_label = "Series"
title = "Series by Mean Rating"
series_ratings = make_plot(series_ratings, x_label, y_label, title, st, kind=charts[select_list])



# # plot 7
st.subheader("Is series more read than non series books?")
select_list = st.selectbox('Select the plot',('Bar','Pie'),key='Pie')
charts = {'Bar':'bar','Pie':'pie'}
series_counts = data.groupby('series').size().sort_values( ascending=False)
y_label = "Count"
x_label = "Series"
title = "Series by Count"
series_ratings = make_plot(series_counts, x_label, y_label, title, st, kind=charts[select_list])


#for next plots
df_genres_rating, df_genres_counts, df_places_rating, df_places_counts = tranform_places_genres(data)

# # plot 8
st.subheader("How Book Volumns Change in Given Year Periods")

df_year = data.original_publish_year

d=data[['original_publish_year','num_pages']].groupby(by='original_publish_year').sum().sort_values('original_publish_year')

select_list = st.selectbox('Select the plot',('Bar','Pie','Line Plot','Horizontal Bar'),key='Lines Plot')
charts = {'Bar':'bar','Pie':'pie','Lines Plot':'line','Horizontal Bar':'barh'}

start = int(st.text_input(label= 'Min Year', value=1999))
time_interval = int(st.text_input(label= 'Year Interval', value=50))
end = int(st.text_input(label= 'Max Year', value=now_year-10))

df_year_pages = d.groupby(pd.cut(d.index, np.arange(start-time_interval, end+time_interval, time_interval))).sum()
y_label = "average rating"
x_label = "year period"
title = "Number of Pages by Year"
make_plot(df_year_pages['num_pages'], x_label, y_label, title, st, kind=charts[select_list])



# # plot 9 Plot Genres and their mean average ratings
st.subheader("Genres More Loved by Readers")
select_list = st.selectbox('Select the plot',('Bar','Pie','Lines','Horizontal Bar'),key='Lines')
charts = {'Bar':'bar','Pie':'pie','Lines':'line','Horizontal Bar':'barh'}
no_of_genres = st.slider('Select number of genres', 1, df_genres_rating['mean_ratings'].shape[0], 10)
y_label = "mean rating"
x_label = "genre"
title = "Genre by Mean Rating"
genres_rating = make_plot(df_genres_rating['mean_ratings'].head(no_of_genres), x_label, y_label, title, st, kind=charts[select_list])

# # plot 10 Plot Genres and their total counts
st.subheader("Genres More Read")
select_list = st.selectbox('Select the plot',('Bar Chart','Pie chart','Lines','Horizontal Bar'),key='Pie chart')
charts = {'Bar Chart':'bar','Pie chart':'pie','Lines':'line','Horizontal Bar':'barh'}
no_of_counts = st.slider('Select number of genres', 1, df_genres_counts['total_counts'].shape[0]+1, 10)
y_label = "counts"
x_label = "genre"
title = "Genre by Counts"
genres_rating = make_plot(df_genres_counts['total_counts'].head(no_of_counts), x_label, y_label, title, st, kind=charts[select_list])


# # plot 10 Plot Places and their mean average ratings
st.subheader("Places With More Loved Books")
select_list = st.selectbox('Select the plot',('Bar Chart','Pie chart','Lines','Horizontal Bar'),key='Bar chart')
charts = {'Bar Chart':'bar','Pie chart':'pie','Lines':'line','Horizontal Bar':'barh'}
no_of_places1= st.slider('Select number of places', 1, df_places_rating['mean_ratings'].shape[0]+2, 10)
y_label = "mean rating"
x_label = "places"
title = "Places by Mean Rating"
places_rating = make_plot(df_places_rating['mean_ratings'].head(no_of_places1), x_label, y_label, title, st, kind=charts[select_list])


# # plot 10 Plot Places and their mean average ratings
st.subheader("Places With More Books")
select_list = st.selectbox('Select the plot',('Bar Charts','Pie charts','Lines','Horizontal Bars'),key='Bar charts')
charts = {'Bar Charts':'bar','Pie charts':'pie','Lines':'line','Horizontal Bars':'barh'}
no_of_places2 = st.slider('Select number of places', 1, df_places_counts['total_counts'].shape[0]+2, 10)
y_label = "counts"
x_label = "places"
title = "Places by Counts"
places_counts= make_plot(df_places_counts['total_counts'].head(no_of_places2), x_label, y_label, title, st, kind=charts[select_list])



# streamlit run best-books-challenge-streamlit.py