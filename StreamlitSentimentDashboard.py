import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt


st.title("Sentinment Analysis of Tweets about US Airlines")

st.sidebar.title("Sentinment Analysis of Tweets about US Airlines")

st.markdown("""Welcome to the Sentiment Analysis Dashboard! This Dashboard allows you to explore and analyze tweets about US airlines, providing insights into public sentiment, tweet locations, and specific reasons for negative feedback. 

Use this dashboard to:

- **Track sentiment trends** over time.
- **Visualize tweet locations** based on the time of day.
- **Analyze negative tweet reasons** by airline.
- **Explore tweet distributions** by sentiment and airline.

Feel free to interact with the filters in the sidebar to tailor the visualizations to your needs. Dive into the data to gain a deeper understanding of customer sentiment!
""")

st.sidebar.markdown("This application is a Streamlit dashboard to analyze the sentiment of Tweets")

DATA_URL = ("https://raw.githubusercontent.com/jwarner3rd/AirlineSentimentAnalysisDashboar/refs/heads/main/data/Tweets.csv")

@st.cache_data(persist=True)
def load_data():
    data = pd.read_csv(DATA_URL)
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data

data = load_data()

st.sidebar.subheader("Show Random Tweet")
random_tweet = st.sidebar.radio('Sentiment', ('positive', 'neutral', 'negative'))
st.sidebar.markdown(data.query('airline_sentiment == @random_tweet')[["text"]].sample(n=1).iat[0,0])

st.sidebar.markdown("### Number of Tweets by Sentiment")
select = st.sidebar.selectbox('Visualization Type', ['Histogram', 'Donut chart'], key='visualization_type')
sentiment_count = data['airline_sentiment'].value_counts()
sentiment_count = pd.DataFrame({'Sentiment':sentiment_count.index, "Tweets":sentiment_count.values})

if not st.sidebar.checkbox("Hide", True):
    st.markdown("### Number of Tweets by Sentiments")
    if select == "Histogram":
        fig = px.bar(sentiment_count, x='Sentiment', y= 'Tweets', color = "Tweets", height=500)
        st.plotly_chart(fig)
    else:
        fig = px.pie(sentiment_count, values='Tweets', names= 'Sentiment', hole=0.4 )
        st.plotly_chart(fig)

st.sidebar.subheader("Sentiment Trend Over Time")

# Add a toggle for Total vs. Airline
trend_view = st.sidebar.radio(
    "View Sentiment Trend for:",
    ["Total Tweets", "Tweets by Airline"]
)

# If viewing by airline, allow selection
selected_airlines = []
if trend_view == "Tweets by Airline":
    selected_airlines = st.sidebar.multiselect(
        "Select Airline(s):",
        data['airline'].unique(),
        default=data['airline'].unique()  # Default to all airlines
    )

# Group and filter data based on user selection
sentiment_time = data.copy()
if trend_view == "Tweets by Airline" and selected_airlines:
    sentiment_time = sentiment_time[sentiment_time['airline'].isin(selected_airlines)]

# Group the data by date and sentiment
sentiment_time_grouped = sentiment_time.groupby(
    [sentiment_time['tweet_created'].dt.date, 'airline_sentiment']
).size().reset_index(name='Tweets')

# Add an airline column if needed
if trend_view == "Tweets by Airline":
    sentiment_time_grouped['airline'] = sentiment_time['airline']

# Plot the data
if not st.sidebar.checkbox("Hide Sentiment Trend", True, key='sentiment_trend_airline'):
    if trend_view == "Tweets by Airline":
        title= " (Filtered by Airline)"
    fig = px.line(
        sentiment_time_grouped,
        x='tweet_created',
        y='Tweets',
        color='airline_sentiment',
        line_group='airline' if trend_view == "Tweets by Airline" else None,
       
        labels={'tweet_created': 'Date', 'Tweets': 'Number of Tweets'},
    )
    st.markdown("### Sentiment Trend Over Time")
    st.plotly_chart(fig)

st.sidebar.subheader("Reasons for Negative Tweets by Airline")

# Filter data for negative sentiment
negative_data = data[data['airline_sentiment'] == 'negative']

# If user selects an airline, filter by that
selected_airlines_for_reasons = st.sidebar.multiselect(
    "Select Airline(s) to Analyze Negative Tweet Reasons:",
    data['airline'].unique(),
    default=data['airline'].unique()  # Default to all airlines
)

# Filter data for selected airlines
negative_data_filtered = negative_data[negative_data['airline'].isin(selected_airlines_for_reasons)]

# Filter data for negative sentiment
negative_data = data[data['airline_sentiment'] == 'negative']

# Filter data for selected airlines
negative_data_filtered = negative_data[negative_data['airline'].isin(selected_airlines_for_reasons)]

# Group by negative reason and airline, then count occurrences
reason_counts = negative_data_filtered.groupby(['airline', 'negativereason']).size().reset_index(name='Count')

# Create a stacked bar chart
if len(selected_airlines_for_reasons) > 0:
    # Create a pivot table where rows are reasons and columns are airlines
    reason_pivot = reason_counts.pivot(index='negativereason', columns='airline', values='Count').fillna(0)

    # Create the pivot table for negative reasons by airline
pivot_table = pd.pivot_table(
    negative_data_filtered[negative_data_filtered['airline_sentiment'] == 'negative'],
    values='text', 
    index='negativereason',
    columns='airline', 
    aggfunc='count',
    fill_value=0
)

# Add row totals (for each airline)
pivot_table['Total per Airline'] = pivot_table.sum(axis=1)

# Add column totals (for each negative reason)
pivot_table.loc['Total per Reason'] = pivot_table.sum(axis=0)

# Display the pivot table
st.markdown("### Negative Tweet Reasons by Airline")
st.write(pivot_table)
    
# Create the stacked bar chart
fig = px.bar(
    reason_pivot,
    x=reason_pivot.index,
    y=reason_pivot.columns,
    labels={'negativereason': 'Reason', 'value': 'Number of Tweets'},
    height=500,
    color_discrete_map={
        'US Airways': '#636EFA',  # Assign same colors as map
        'United': '#EF553B',
        'American': '#00CC96',
        'Southwest': '#AB63FA',
        'Delta': '#FFA15C',
        'Virgin America': '#19D3F3'
        }
    )

fig.update_layout(barmode='stack')
st.markdown("### Negative Tweet Reasons by Airline")
st.plotly_chart(fig)

st.sidebar.subheader("When and Where are Users Tweeting From?")

# Hour filter
hour = st.sidebar.slider("Hour of Day", 0, 23)

# Sentiment filter
sentiment_options = ['positive', 'neutral', 'negative']
selected_sentiment = st.sidebar.multiselect("Filter by Sentiment", sentiment_options, default=sentiment_options)

# Airline filter
airline_options = data['airline'].unique()
selected_airlines = st.sidebar.multiselect("Filter by Airline", airline_options, default=airline_options)

# Filter data based on selections
filtered_data = data[
    (data['tweet_created'].dt.hour == hour) &
    (data['airline_sentiment'].isin(selected_sentiment)) &
    (data['airline'].isin(selected_airlines))
]

if not st.sidebar.checkbox("Close", True, key='1'):
    st.markdown(f"### Tweets locations ({hour}:00 - {(hour+1)%24}:00)")
    st.markdown(f"{len(filtered_data)} tweets match the selected criteria")

    if len(filtered_data) > 0:
        # Create map with tooltips and color-coded points
        fig = px.scatter_mapbox(
            filtered_data,
            lat="latitude",
            lon="longitude",
            color="airline",  # Color by airline
            hover_name="text",  # Show tweet text as tooltip
            hover_data={
                "airline_sentiment": True,
                "airline": True,
                "latitude": False,
                "longitude": False
            },
            title="Tweet Locations",
            mapbox_style="carto-positron",
            height=600,
            width=800,
            zoom=3,
        )
        st.plotly_chart(fig)
    else:
        st.write("No tweets available for the selected criteria.")

    if st.sidebar.checkbox("Show raw data", False):
        st.write(filtered_data)

st.sidebar.subheader("Breakdown Airline Tweets by Sentiment")
choice = st.sidebar.multiselect('Pick airline', ('US Airways', 'United', 'American', 'Southwest', 'Delta', 'Virgin America'), key= '0')

if len(choice) > 0:
    choice_data = data[data.airline.isin(choice)]
    fig_choice = px.histogram(choice_data, x='airline', y='airline_sentiment', histfunc='count', color= 'airline_sentiment',
    facet_col='airline_sentiment', labels={'airline_sentiment':'tweets'}, height=600, width=800)
    st.plotly_chart(fig_choice)

st.sidebar.header("Word Cloud")
word_sentiment = st.sidebar.radio('Display Word Cloud for What Sentiment?', ('positive', 'neutral', 'negative'))

if not st.sidebar.checkbox("Closed", True, key='3'):
    st.header('Word cloud for %s sentiment' % (word_sentiment))
    df = data[data['airline_sentiment']==word_sentiment]
    words = ' '.join(df['text'])
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
    
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color= 'white', height = 640, width=800).generate(processed_words)

    fig, ax = plt.subplots()
    plt.imshow(wordcloud)
    ax.axis('off')
    #plt.xticks([])
    #plt.yticks([])
    st.pyplot(fig)
    fig, ax = plt.subplots()




