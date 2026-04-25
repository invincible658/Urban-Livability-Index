import streamlit as st
import pandas as pd

# Load dataset
df = pd.read_csv("final_livability_data.csv")

st.title("Urban Livability Recommender")
st.write("Find the best area to live in Pune based on your preferences.")

# --- Global Normalization ---
# We normalize against the FULL dataset so that each area's score is
# absolute, not relative to the filtered subset. This prevents the
# cheapest area from always winning after filtering.

def normalize(col):
    if col.max() == col.min():
        return col * 0.0
    return (col - col.min()) / (col.max() - col.min())

df["g_price_norm"]      = normalize(df["price_per_sqft"])
df["g_aqi_norm"]        = normalize(df["aqi"])
df["g_congestion_norm"] = normalize(df["congestion_score"])
df["g_growth_norm"]     = normalize(df["growth_score"])

# Invert metrics where lower is better (price, aqi, congestion)
# so that a score of 1.0 = best
df["g_price_score"]      = 1 - df["g_price_norm"]
df["g_aqi_score"]        = 1 - df["g_aqi_norm"]
df["g_congestion_score"] = 1 - df["g_congestion_norm"]
df["g_growth_score"]     = df["g_growth_norm"]  # higher growth is better


# --- User Inputs (Filters) ---
st.subheader("Set your filters")

budget = st.slider(
    "Max Price (Rs/sqft)",
    int(df["price_per_sqft"].min()),
    int(df["price_per_sqft"].max()),
    int(df["price_per_sqft"].max()),
    step=500
)

max_aqi = st.slider(
    "Max AQI",
    int(df["aqi"].min()),
    int(df["aqi"].max()),
    int(df["aqi"].max()),
    step=5
)

max_congestion = st.slider(
    "Max Congestion Score",
    int(df["congestion_score"].min()),
    int(df["congestion_score"].max()),
    int(df["congestion_score"].max())
)


# --- User Inputs (Weights) ---
st.subheader("Set your priorities")
st.write("How important is each factor to you?")

price_w = st.slider("Importance of Price",      0.0, 1.0, 0.30, 0.05)
aqi_w   = st.slider("Importance of Air Quality", 0.0, 1.0, 0.25, 0.05)
cong_w  = st.slider("Importance of Congestion",  0.0, 1.0, 0.20, 0.05)
grow_w  = st.slider("Importance of Growth",       0.0, 1.0, 0.25, 0.05)

# Normalize weights so they always add up to 1
total_w = price_w + aqi_w + cong_w + grow_w
if total_w == 0:
    total_w = 1.0
price_w = price_w / total_w
aqi_w   = aqi_w   / total_w
cong_w  = cong_w  / total_w
grow_w  = grow_w  / total_w

st.write(
    f"Effective weights: Price {price_w:.0%}, AQI {aqi_w:.0%}, "
    f"Congestion {cong_w:.0%}, Growth {grow_w:.0%}"
)


# --- Apply Filters ---
filtered = df[
    (df["price_per_sqft"]   <= budget) &
    (df["aqi"]              <= max_aqi) &
    (df["congestion_score"] <= max_congestion)
].copy()


# Recommendation logic
if not filtered.empty:

    filtered["dynamic_score"] = (
        price_w * filtered["g_price_score"] +
        aqi_w   * filtered["g_aqi_score"] +
        cong_w  * filtered["g_congestion_score"] +
        grow_w  * filtered["g_growth_score"]
    )

    filtered = filtered.sort_values("dynamic_score", ascending=False)

    # Top recommendation
    best = filtered.iloc[0]
    st.success(f"Recommended Area: {best['area_name']}")

    # Show details of best area
    st.subheader("Best Area Details")
    st.write(f"- Price per sqft: Rs {int(best['price_per_sqft'])}")
    st.write(f"- AQI: {int(best['aqi'])}")
    st.write(f"- Congestion Score: {int(best['congestion_score'])}")
    st.write(f"- Growth Score: {int(best['growth_score'])}")
    st.write(f"- Livability Score: {best['dynamic_score']:.3f}")

    # Show all ranked results
    st.subheader("All Matching Areas (Ranked)")
    results = filtered[["area_name", "price_per_sqft", "aqi",
                         "congestion_score", "growth_score",
                         "dynamic_score"]].copy()
    results.columns = ["Area", "Price/sqft", "AQI", "Congestion",
                        "Growth", "Score"]
    results.index = range(1, len(results) + 1)
    results.index.name = "Rank"
    st.dataframe(results)

    # Simple bar chart of scores
    st.subheader("Score Comparison")
    chart_data = results.set_index("Area")[["Score"]]
    st.bar_chart(chart_data)

else:
    st.warning("No area matches your preferences. Try relaxing the filters.")