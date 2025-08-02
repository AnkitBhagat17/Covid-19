import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(page_title="COVID-19 Data Dashboard", layout="wide")
st.title("🦠 COVID-19 Analysis and Visualization")

# Load Data
@st.cache_data
def load_data():
    # url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    df = pd.read_csv("owid-covid-data.csv", parse_dates=['date'])
    df = df[['location', 'date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths', 'total_tests']]
    df.dropna(subset=["total_cases"], inplace=True)
    return df

df = load_data()

# Sidebar
st.sidebar.header("🔍 Filter Data")
countries = sorted(df['location'].unique())
selected_country = st.sidebar.selectbox("Select a Country", countries)

# Country Data
country_data = df[df['location'] == selected_country].sort_values("date")
latest = country_data.iloc[-1]

# KPIs
st.subheader(f"📌 Key Statistics for {selected_country}")
col1, col2, col3 = st.columns(3)
col1.metric("📈 Total Cases", f"{int(latest.total_cases):,}")
col2.metric("💀 Total Deaths", f"{int(latest.total_deaths):,}" if pd.notna(latest.total_deaths) else "N/A")
col3.metric("🧪 Total Tests", f"{int(latest.total_tests):,}" if pd.notna(latest.total_tests) else "N/A")

# Total Cases
st.subheader(f"📊 Total COVID-19 Cases Over Time in {selected_country}")
fig_cases = px.line(country_data, x='date', y='total_cases', template="plotly_dark")
st.plotly_chart(fig_cases, use_container_width=True)

# New Cases
st.subheader(f"📉 New COVID-19 Cases per Day in {selected_country}")
fig_new_cases = px.bar(country_data, x='date', y='new_cases', template="plotly_dark")
st.plotly_chart(fig_new_cases, use_container_width=True)

# Total Deaths
if country_data['total_deaths'].notna().sum() > 0:
    st.subheader(f"☠️ Total COVID-19 Deaths Over Time in {selected_country}")
    fig_deaths = px.line(country_data, x='date', y='total_deaths', template="plotly_dark")
    st.plotly_chart(fig_deaths, use_container_width=True)
else:
    st.warning("⚠️ Death data not available for this country.")

# New Cases vs New Deaths Scatter
st.subheader("📍 New Cases vs New Deaths")
scatter_df = country_data.dropna(subset=['new_cases', 'new_deaths'])
fig_scatter = px.scatter(scatter_df, x='new_cases', y='new_deaths', color='new_deaths',
                         title="New Cases vs New Deaths", size='new_cases', template='plotly_white')
st.plotly_chart(fig_scatter, use_container_width=True)

# 7-day Moving Average of New Cases
st.subheader("📊 7-Day Moving Average of New Cases")
country_data['7_day_avg'] = country_data['new_cases'].rolling(window=7).mean()
fig_avg, ax_avg = plt.subplots(figsize=(10, 4))
ax_avg.plot(country_data['date'], country_data['7_day_avg'], color='green', label='7-Day Avg')
ax_avg.set_title("7-Day Moving Average")
ax_avg.set_xlabel("Date")
ax_avg.set_ylabel("Cases")
ax_avg.legend()
st.pyplot(fig_avg)

# Pie Chart: Total Cases vs Deaths vs Tests
st.subheader("🥧 Proportion of COVID Stats")
pie_values, pie_labels = [], []
if not pd.isna(latest.total_cases): pie_values.append(latest.total_cases); pie_labels.append("Cases")
if not pd.isna(latest.total_deaths): pie_values.append(latest.total_deaths); pie_labels.append("Deaths")
if not pd.isna(latest.total_tests): pie_values.append(latest.total_tests); pie_labels.append("Tests")
fig_pie = px.pie(values=pie_values, names=pie_labels, hole=0.3, title="COVID Data Proportion")
st.plotly_chart(fig_pie, use_container_width=True)

# Top 10 Days with Highest New Cases
st.subheader("🔝 Top 10 Days with Highest New Cases")
top10 = country_data.sort_values('new_cases', ascending=False).head(10)
fig_top, ax_top = plt.subplots(figsize=(10, 4))
ax_top.bar(top10['date'].dt.strftime('%Y-%m-%d'), top10['new_cases'], color='orange')
ax_top.set_title("Top 10 Days with Highest New Cases")
ax_top.set_ylabel("New Cases")
ax_top.set_xticklabels(top10['date'].dt.strftime('%Y-%m-%d'), rotation=45)
st.pyplot(fig_top)

# Total Cases vs Deaths Over Time
st.subheader("📉 Total Cases and Deaths Over Time")
fig_combine = px.line(country_data, x='date', y=['total_cases', 'total_deaths'],
                      labels={"value": "Count", "variable": "Metric"}, template="plotly_white")
st.plotly_chart(fig_combine, use_container_width=True)

# Global Map
st.subheader("🌍 Global Total Cases Map")
latest_global = df.sort_values("date").groupby("location").tail(1)
map_df = latest_global[["location", "total_cases"]].dropna()
fig_map = px.choropleth(map_df, locations="location", locationmode="country names", color="total_cases",
                        color_continuous_scale="Reds", title="Global COVID-19 Total Cases")
st.plotly_chart(fig_map, use_container_width=True)

# Country Comparison
st.subheader("🔁 Compare Countries (Total Cases)")
multi_country = st.multiselect("Choose countries", countries, default=["India", "United States", "Brazil"])
compare_df = df[df['location'].isin(multi_country)].dropna(subset=['total_cases'])
fig_compare = px.line(compare_df, x='date', y='total_cases', color='location',
                      title="Comparison of Total Cases", template="plotly_white")
st.plotly_chart(fig_compare, use_container_width=True)

# Download CSV
st.subheader("💾 Download Data")
csv_data = country_data.to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Download Country Data as CSV",
                   data=csv_data,
                   file_name=f"{selected_country}_covid_data.csv",
                   mime='text/csv')

# Optional: Animated Global Spread
with st.expander("🌐 Animated Global Spread (Slow Internet? Skip this)"):
    animated_df = df[df['date'] >= "2020-03-01"].dropna(subset=['total_cases'])
    fig_animated = px.choropleth(animated_df,
                                  locations="location",
                                  locationmode="country names",
                                  color="total_cases",
                                  hover_name="location",
                                  animation_frame=animated_df['date'].dt.strftime('%Y-%m-%d'),
                                  color_continuous_scale="viridis",
                                  title="Animated Global Spread Over Time")
    st.plotly_chart(fig_animated, use_container_width=True)

# Show Raw Data
with st.expander("📋 View Raw Data"):
    st.dataframe(country_data.tail(20))
