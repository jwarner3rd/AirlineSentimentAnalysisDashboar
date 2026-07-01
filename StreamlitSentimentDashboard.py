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

DATA_URL = "https://raw.githubusercontent.com/jwarner3rd/AirlineSentimentAnalysisDashboard/refs/heads/main/data/Tweets.csv"


def first_matching_column(columns, candidates):
    normalized_columns = {str(column).strip().lower(): column for column in columns}
    for candidate in candidates:
        if candidate in normalized_columns:
            return normalized_columns[candidate]
    return None


def normalize_tweet_data(source_data):
    data = source_data.copy()
    rename_map = {}

    text_column = first_matching_column(
        data.columns,
        ["text", "tweet", "tweet_text", "full_text", "content", "message"]
    )
    sentiment_column = first_matching_column(
        data.columns,
        ["airline_sentiment", "sentiment", "predicted_sentiment", "label"]
    )
    created_column = first_matching_column(
        data.columns,
        ["tweet_created", "created_at", "createdat", "date", "timestamp"]
    )
    airline_column = first_matching_column(data.columns, ["airline", "carrier"])

    if text_column and text_column != "text":
        rename_map[text_column] = "text"
    if sentiment_column and sentiment_column != "airline_sentiment":
        rename_map[sentiment_column] = "airline_sentiment"
    if created_column and created_column != "tweet_created":
        rename_map[created_column] = "tweet_created"
    if airline_column and airline_column != "airline":
        rename_map[airline_column] = "airline"

    data = data.rename(columns=rename_map)
    missing_columns = sorted({"text", "airline_sentiment"}.difference(data.columns))
    if missing_columns:
        raise ValueError(", ".join(missing_columns))

    if "tweet_created" in data:
        data["tweet_created"] = pd.to_datetime(data["tweet_created"], errors="coerce")
    else:
        data["tweet_created"] = pd.Timestamp.utcnow()

    if "airline" not in data:
        data["airline"] = "Unknown"

    if "negativereason" not in data:
        data["negativereason"] = "Not provided"

    data = data.dropna(subset=["text", "airline_sentiment", "tweet_created"])
    data["airline_sentiment"] = data["airline_sentiment"].astype(str).str.lower()
    return data

@st.cache_data(persist=True)
def load_default_data():
    try:
        return normalize_tweet_data(pd.read_csv(DATA_URL))
    except Exception:
        return normalize_tweet_data(pd.read_csv("data/Tweets.csv"))

uploaded_csv = st.sidebar.file_uploader(
    "Upload a compatible tweet CSV",
    type=["csv"],
    help="Use columns such as text, sentiment, tweet_created, and airline."
)

try:
    if uploaded_csv is None:
        data = load_default_data()
    else:
        data = normalize_tweet_data(pd.read_csv(uploaded_csv))
except Exception as exc:
    st.error(f"Could not load tweet data. Missing or invalid column: {exc}")
    st.stop()

st.sidebar.subheader("Show Random Tweet")
sentiment_options = sorted(data['airline_sentiment'].dropna().unique().tolist())
random_tweet = st.sidebar.radio('Sentiment', sentiment_options)
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
    airline_options = sorted(data['airline'].dropna().unique().tolist())
    selected_airlines = st.sidebar.multiselect(
        "Select Airline(s):",
        airline_options,
        default=airline_options
    )

# Group and filter data based on user selection
sentiment_time = data.copy()
if trend_view == "Tweets by Airline" and selected_airlines:
    sentiment_time = sentiment_time[sentiment_time['airline'].isin(selected_airlines)]

if trend_view == "Tweets by Airline":
    sentiment_time_grouped = sentiment_time.groupby(
        [sentiment_time['tweet_created'].dt.date, 'airline', 'airline_sentiment']
    ).size().reset_index(name='Tweets')
else:
    sentiment_time_grouped = sentiment_time.groupby(
        [sentiment_time['tweet_created'].dt.date, 'airline_sentiment']
    ).size().reset_index(name='Tweets')

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
    sorted(data['airline'].dropna().unique().tolist()),
    default=sorted(data['airline'].dropna().unique().tolist())
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
selected_sentiment = st.sidebar.multiselect("Filter by Sentiment", sentiment_options, default=sentiment_options)

# Airline filter
airline_options = sorted(data['airline'].dropna().unique().tolist())
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

    if len(filtered_data) > 0 and {"latitude", "longitude"}.issubset(filtered_data.columns):
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
    elif len(filtered_data) > 0:
        st.write("Upload latitude and longitude columns to enable the map view.")
    else:
        st.write("No tweets available for the selected criteria.")

    if st.sidebar.checkbox("Show raw data", False):
        st.write(filtered_data)

st.sidebar.subheader("Breakdown Airline Tweets by Sentiment")
choice = st.sidebar.multiselect('Pick airline', airline_options, key= '0')

if len(choice) > 0:
    choice_data = data[data.airline.isin(choice)]
    fig_choice = px.histogram(choice_data, x='airline', y='airline_sentiment', histfunc='count', color= 'airline_sentiment',
    facet_col='airline_sentiment', labels={'airline_sentiment':'tweets'}, height=600, width=800)
    st.plotly_chart(fig_choice)

st.sidebar.header("Word Cloud")
word_sentiment = st.sidebar.radio('Display Word Cloud for What Sentiment?', sentiment_options)

if not st.sidebar.checkbox("Closed", True, key='3'):
    st.header('Word cloud for %s sentiment' % (word_sentiment))
    df = data[data['airline_sentiment']==word_sentiment]
    words = ' '.join(df['text'])
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
    if processed_words.strip():
        wordcloud = WordCloud(stopwords=STOPWORDS, background_color= 'white', height = 640, width=800).generate(processed_words)

        fig, ax = plt.subplots()
        plt.imshow(wordcloud)
        ax.axis('off')
        #plt.xticks([])
        #plt.yticks([])
        st.pyplot(fig)
        fig, ax = plt.subplots()
    else:
        st.info("No text is available for the selected sentiment.")
