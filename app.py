import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Load the data
@st.cache_data
def load_data(file_path):
    """
    Load the CSV file into a DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


# Main function
def main():
    st.title("Google Maps Reviews Dashboard")
    st.write("Analyze locations, ratings, and reviews data extracted via Google Places API.")

    # Load data from specified location
    file_path_1 = "data/naturals_chennai_locations_metadata.csv"
    ratings_df = load_data(file_path_1)
    ratings_df["full_location"] = ratings_df["City Area"] + ratings_df["Name"]

    file_path_2 = "data/naturals_reviews.csv"
    reviews_df = load_data(file_path_2)

    file_path_3 = "data/naturals_sentiments.csv"
    sentiments_df = load_data(file_path_3)

    df = pd.merge(ratings_df, sentiments_df, left_on="Place ID", right_on="place_id", how="right")
    df = df[df["caption"].notna()]

    if not ratings_df.empty and not reviews_df.empty and not sentiments_df.empty:
        st.success("Data loaded successfully!")
    else:
        st.warning("The file is empty or has an unexpected format. Please check the file.")

    # Display metrics
    st.header("Key Metrics")

    M1, M2 = st.columns(2)
    m1, m2, m3 = M1.columns(3)
    # Total number of locations
    total_locations = len(df['place_id'].unique())
    m1.metric(label="Total Locations", value=total_locations)

    # Average Rating
    average_rating = df["Rating"].mean()
    m2.metric(label="Overall Average Rating", value=f"{average_rating:.2f}")

    # Total Reviews (sum of Total Reviews column)
    total_reviews = df['caption'].notna().sum()
    m3.metric(label="Total Number of Reviews", value=total_reviews)

    #### CHARTS ####
    col1, col2, col3 = st.columns(3)

    # CHART 1
    category_counts = df['Rating'].value_counts().reset_index()
    category_counts.columns = ['rating', 'count']
    # Create the pie chart
    fig = px.pie(category_counts,
                 names='rating',  # Labels for the pie chart
                 values='count',  # Sizes of the pie chart slices
                 title='Salon Rating Distribution')
    # Display the chart in Streamlit
    col1.plotly_chart(fig, theme="streamlit")

    # CHART 2
    category_counts = df['rating'].value_counts().reset_index()
    category_counts.columns = ['rating', 'count']
    # Create the pie chart
    fig = px.pie(category_counts,
                 names='rating',  # Labels for the pie chart
                 values='count',  # Sizes of the pie chart slices
                 title='User Rating Distribution')
    # Display the chart in Streamlit
    col2.plotly_chart(fig, theme="streamlit")

    # CHART 3: Sentiment Distribution as a Bar Chart
    category_counts = sentiments_df['sentiment'].value_counts().reset_index()
    category_counts.columns = ['sentiment', 'count']
    fig = px.bar(category_counts,
                 x='sentiment',  # Sentiment categories on the x-axis
                 y='count',  # Counts on the y-axis
                 title='Sentiment Distribution',
                 text='count')  # Display counts on the bars
    col3.plotly_chart(fig, theme="streamlit")

    # Display top five locations with least rating
    st.header("Top 5 Locations with Least Rating")
    top_least_rated = ratings_df.sort_values(by="Rating", ascending=True).head(5)
    st.dataframe(top_least_rated[["City Area", "Name", "Rating", "Total Reviews", "Address"]])




    col1, col2 = st.columns(2)
    timeline = col1.selectbox("Select Timeline", options=reviews_df["relative_date"].unique())
    rating = col2.slider(
        "Select Rating",
        min_value=0,  # Minimum value for the slider
        max_value=5,  # Maximum value for the slider
        value=0,  # Default value
        step=1  # Step size for the slider
    )

    filtered_df = df[(df['relative_date'] == timeline) & (df['rating'] == rating)]
    st.dataframe(filtered_df[["City Area", "Name", "Address", "caption", "rating"]])


    selected_location = st.selectbox("Select a Naturals Location", options=df['full_location'].unique())

    if selected_location:
        filtered_df = df[df['full_location'] == selected_location]

        # Calculate value counts for the pie chart
        category_counts = filtered_df['sentiment'].value_counts().reset_index()
        category_counts.columns = ['sentiment', 'count']

        # Create the pie chart
        fig = px.pie(category_counts,
                     names='sentiment',  # Labels for the pie chart
                     values='count',  # Sizes of the pie chart slices
                     title='Sentiment Distribution')

        # Display the chart in Streamlit
        st.plotly_chart(fig)

    else:
        # Calculate value counts for the pie chart
        category_counts = df['sentiment'].value_counts().reset_index()
        category_counts.columns = ['sentiment', 'count']

        # Create the pie chart
        fig = px.pie(category_counts,
                     names='sentiment',  # Labels for the pie chart
                     values='count',  # Sizes of the pie chart slices
                     title='Sentiment Distribution')

        # Display the chart in Streamlit
        st.plotly_chart(fig)

# Run the app
if __name__ == "__main__":
    main()
