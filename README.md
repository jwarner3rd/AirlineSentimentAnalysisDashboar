# Airline Sentiment Analysis Dashboard

This project is based on the Coursera course ["Create Interactive Dashboards with Streamlit and Python"](https://www.coursera.org/projects/interactive-dashboards-streamlit-python) by instructor Snehan Kekre.. It provides an interactive dashboard for analyzing sentiment in tweets about US airlines. The dashboard visualizes various insights, including sentiment distribution, tweet locations, and reasons behind negative sentiments.

## Updates From the Orginal Project

Some updates from the orginal project include:

- **Sentiment Trend Over Time**: A dynamic line chart showing how sentiment trends over time for all tweets or filtered by airline.
 ![Trend Over Time](image/lineovertime.png)
- **Reasons for Negative Tweets by Airline**: A pivot table displaying the top reasons for negative tweets by airline, along with a stacked bar chart showing the reasons for each airline. This helps identify patterns in customer complaints.
![Negative Tweets](image/stackedbar.png)
- **Updated Tweet Map**: Tweets are plotted on an interactive map with color coding by airline. The tooltips display the sentiment type and tweet content, making it easy to understand user sentiment in different regions.
![Tweet Map](image/stackedbar.png)

#### Visualizations:

- **Sentiment Distribution**: Donut chart and histogram to visualize the sentiment breakdown of tweets.

## Dataset
The dataset consists of tweets about US airlines and includes various columns such as sentiment, tweet text, tweet creation time, and more. The data is fetched directly from the GitHub repository folder: [Here](https://github.com/jwarner3rd/AirlineSentimentAnalysisDashboard/tree/main/data)
.
