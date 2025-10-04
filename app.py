# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="E-Commerce Metrics & Business Analytics Dashboard - 2024", layout="wide")
st.title("📊 E-Commerce Metrics & Business Analytics Dashboard — 2024")

# ---------- Helpers ----------
@st.cache_data
def load_sample_data():
    data = {
        "Month": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "Visitors": [4800,5100,5300,5500,5800,6000,6300,6500,6700,7000,7200,7500],
        "Conversion_Rate (%)": [4.8,5.1,5.3,5.5,5.7,5.9,6.0,6.2,6.4,6.5,6.7,6.9],
        "Sales_Closed": [230,260,280,300,330,350,380,400,430,460,480,510],
        "Cash_Sale (PKR)": [450000,520000,580000,620000,700000,760000,820000,880000,940000,1000000,1060000,1150000],
        "Bank_Sale (PKR)": [700000,800000,870000,980000,1050000,1130000,1230000,1320000,1440000,1550000,1640000,1750000],
        "Calls_Made":[180,200,210,230,250,260,280,290,310,330,340,360],
        "Likes":[290,320,340,360,380,400,420,440,460,480,500,520],
        "Engagement_Rate (%)":[6.5,7.0,7.2,7.5,7.7,7.9,8.0,8.2,8.3,8.5,8.6,8.8]
    }
    df = pd.DataFrame(data)
    df["Revenue (PKR)"] = df["Cash_Sale (PKR)"] + df["Bank_Sale (PKR)"]
    return df

def compute_insights(df):
    insights = []
    # YTD totals
    ytd_rev = df["Revenue (PKR)"].sum()
    ytd_vis = df["Visitors"].sum()
    avg_conv = df["Conversion_Rate (%)"].mean()
    insights.append(f"YTD Revenue: PKR {ytd_rev:,}")
    insights.append(f"YTD Visitors: {ytd_vis:,}")
    insights.append(f"Average Conversion Rate: {avg_conv:.2f}%")
    # best month by revenue
    best_rev_row = df.loc[df["Revenue (PKR)"].idxmax()]
    insights.append(f"Top month by revenue: {best_rev_row['Month']} (PKR {int(best_rev_row['Revenue (PKR)']):,})")
    # cash vs bank share
    total_cash = df["Cash_Sale (PKR)"].sum()
    total_bank = df["Bank_Sale (PKR)"].sum()
    cash_share = total_cash / (total_cash + total_bank) * 100
    insights.append(f"Cash vs Bank split: Cash {cash_share:.1f}% / Bank {100-cash_share:.1f}%")
    return insights

# ---------- Load Data ----------
st.sidebar.header("Data Source")
use_sample = st.sidebar.checkbox("Use built-in sample data (ecommerce_2024.csv)", value=True)
uploaded_file = st.sidebar.file_uploader("Or upload your CSV file", type=["csv"])

if use_sample or uploaded_file is None:
    df = load_sample_data()
else:
    try:
        df = pd.read_csv(uploaded_file)
        # If Revenue not present, try to compute
        if "Revenue (PKR)" not in df.columns and "Cash_Sale (PKR)" in df.columns and "Bank_Sale (PKR)" in df.columns:
            df["Revenue (PKR)"] = df["Cash_Sale (PKR)"] + df["Bank_Sale (PKR)"]
    except Exception as e:
        st.error(f"Failed to read uploaded file: {e}")
        st.stop()

# ---------- Global Filters ----------
st.sidebar.markdown("### Filters")
months = ["All"] + list(df["Month"].astype(str))
selected_month = st.sidebar.selectbox("Select Month", months, index=0)
min_visitors = int(df["Visitors"].min())
max_visitors = int(df["Visitors"].max())
vis_range = st.sidebar.slider("Visitors range", min_visitors, max_visitors, (min_visitors, max_visitors))

# apply filters
filtered = df.copy()
if selected_month != "All":
    filtered = filtered[filtered["Month"] == selected_month]
filtered = filtered[(filtered["Visitors"] >= vis_range[0]) & (filtered["Visitors"] <= vis_range[1])]

# ---------- Tabs ----------
tab_overview, tab_sales, tab_marketing, tab_ops = st.tabs(["🏠 Overview", "💼 Sales", "📣 Marketing", "🛠️ Operations"])

with tab_overview:
    st.subheader("Overview")
    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Visitors", f"{filtered['Visitors'].sum():,}")
    col2.metric("📈 Avg Conversion Rate", f"{filtered['Conversion_Rate (%)'].mean():.2f}%")
    col3.metric("💼 Sales Closed", f"{filtered['Sales_Closed'].sum():,}")
    col4.metric("💰 Revenue (PKR)", f"{filtered['Revenue (PKR)'].sum():,}")
    st.write("")
    # Insights
    st.markdown("### 🔎 Insights")
    for insight in compute_insights(filtered):
        st.write("•", insight)
    st.markdown("---")
    # Revenue and Visitors trend
    c1, c2 = st.columns(2)
    fig_rev = px.line(df, x="Month", y="Revenue (PKR)", markers=True, title="Monthly Revenue (PKR)")
    c1.plotly_chart(fig_rev, use_container_width=True)
    fig_vis = px.bar(df, x="Month", y="Visitors", title="Monthly Visitors", text_auto=True)
    c2.plotly_chart(fig_vis, use_container_width=True)

with tab_sales:
    st.subheader("Sales Performance")
    # Cash vs Bank stacked bar
    fig_cb = px.bar(df, x="Month", y=["Cash_Sale (PKR)", "Bank_Sale (PKR)"],
                    title="Cash vs Bank Sales by Month", barmode="stack")
    st.plotly_chart(fig_cb, use_container_width=True)
    # Table and summary
    st.markdown("**Monthly Sales Table**")
    st.dataframe(filtered[["Month","Sales_Closed","Cash_Sale (PKR)","Bank_Sale (PKR)","Revenue (PKR)"]].reset_index(drop=True))
    # Top months
    st.markdown("**Top 3 Months by Revenue**")
    top3 = df.sort_values("Revenue (PKR)", ascending=False).head(3)
    st.table(top3[["Month","Revenue (PKR)"]].assign(**{"Revenue (PKR)": top3["Revenue (PKR)"].map(lambda x: f"PKR {int(x):,}")}))

with tab_marketing:
    st.subheader("Marketing & Engagement")
    col1, col2 = st.columns([2,1])
    fig_eng = px.line(df, x="Month", y="Engagement_Rate (%)", title="Engagement Rate (%)", markers=True)
    col1.plotly_chart(fig_eng, use_container_width=True)
    fig_likes = px.bar(df, x="Month", y="Likes", title="Likes by Month", text_auto=True)
    col2.plotly_chart(fig_likes, use_container_width=True)
    st.markdown("**Conversion vs Engagement**")
    fig_conv = px.scatter(df, x="Engagement_Rate (%)", y="Conversion_Rate (%)", size="Visitors",
                          hover_name="Month", title="Conversion vs Engagement (bubble size = Visitors)")
    st.plotly_chart(fig_conv, use_container_width=True)

with tab_ops:
    st.subheader("Operations")
    st.markdown("Calls and Activity")
    fig_calls = px.bar(df, x="Month", y="Calls_Made", title="Calls Made by Month", text_auto=True)
    st.plotly_chart(fig_calls, use_container_width=True)
    st.markdown("**Calls vs Sales Closed**")
    fig_calls_sales = px.line(df, x="Month", y=["Calls_Made","Sales_Closed"], title="Calls Made vs Sales Closed", markers=True)
    st.plotly_chart(fig_calls_sales, use_container_width=True)
    st.markdown("**Export / Download**")
    # Download filtered data
    to_download = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered Data (CSV)", data=to_download, file_name="filtered_ecommerce_kpis.csv", mime="text/csv")

# ---------- Footer ----------
st.markdown("---")
st.markdown("Built for demo uploaded by Talha Mehmood — sample data (2024, PKR). Upload your CSV to analyze your own data.")
