
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(r"global_power_plant_database.csv")
    return df

df = load_data()
df.columns = df.columns.str.strip()

total_plants = len(df)

# ─────────────────────────────────────────────
# 2. SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.header("Filters")

# Country
country_list = sorted(df["country_long"].dropna().unique().tolist())
select_all_country = st.sidebar.checkbox("Select All Countries")
selected_country = st.sidebar.multiselect(
    "Select Country",
    country_list,
    default=country_list if select_all_country else []
)

# Primary Fuel
primary_fuel_list = sorted(df["primary_fuel"].dropna().unique().tolist())
select_all_primary = st.sidebar.checkbox("Select All Primary Fuels")
selected_primary = st.sidebar.multiselect(
    "Primary Fuel",
    primary_fuel_list,
    default=primary_fuel_list if select_all_primary else []
)

# Other Fuel 1
other1_list = sorted(df["other_fuel1"].fillna("NaN").unique().tolist())
select_all_other1 = st.sidebar.checkbox("Select All Other_Fuel_1")
selected_other1 = st.sidebar.multiselect(
    "Other Fuel 1",
    other1_list,
    default=other1_list if select_all_other1 else []
)

# Other Fuel 2
other2_list = sorted(df["other_fuel2"].fillna("NaN").unique().tolist())
select_all_other2 = st.sidebar.checkbox("Select All Other_Fuel_2")
selected_other2 = st.sidebar.multiselect(
    "Other Fuel 2",
    other2_list,
    default=other2_list if select_all_other2 else []
)

# Other Fuel 3
other3_list = sorted(df["other_fuel3"].fillna("NaN").unique().tolist())
select_all_other3 = st.sidebar.checkbox("Select All Other_Fuel_3")
selected_other3 = st.sidebar.multiselect(
    "Other Fuel 3",
    other3_list,
    default=other3_list if select_all_other3 else []
)

# ─────────────────────────────────────────────
# 3. FILTER CHECK
# ─────────────────────────────────────────────
no_filter_selected = (
    len(selected_country) == 0 and
    len(selected_primary) == 0 and
    len(selected_other1) == 0 and
    len(selected_other2) == 0 and
    len(selected_other3) == 0
)

# ─────────────────────────────────────────────
# 4. TITLE
# ─────────────────────────────────────────────
st.title("🌍 Global Power Plants Dashboard")

# ─────────────────────────────────────────────
# 5. DATA PREPARATION
# ─────────────────────────────────────────────
filtered_df = df.copy()

if not no_filter_selected:

    if selected_country:
        filtered_df = filtered_df[filtered_df["country_long"].isin(selected_country)]

    if selected_primary:
        filtered_df = filtered_df[filtered_df["primary_fuel"].isin(selected_primary)]

    # Other Fuel 1
    if selected_other1:
        mask = pd.Series(False, index=filtered_df.index)
        if "NaN" in selected_other1:
            mask |= filtered_df["other_fuel1"].isna()
        mask |= filtered_df["other_fuel1"].isin([x for x in selected_other1 if x != "NaN"])
        filtered_df = filtered_df[mask]

    # Other Fuel 2
    if selected_other2:
        mask = pd.Series(False, index=filtered_df.index)
        if "NaN" in selected_other2:
            mask |= filtered_df["other_fuel2"].isna()
        mask |= filtered_df["other_fuel2"].isin([x for x in selected_other2 if x != "NaN"])
        filtered_df = filtered_df[mask]

    # Other Fuel 3
    if selected_other3:
        mask = pd.Series(False, index=filtered_df.index)
        if "NaN" in selected_other3:
            mask |= filtered_df["other_fuel3"].isna()
        mask |= filtered_df["other_fuel3"].isin([x for x in selected_other3 if x != "NaN"])
        filtered_df = filtered_df[mask]

# Clean data
filtered_df = filtered_df.dropna(subset=["latitude", "longitude"])
filtered_df = filtered_df[filtered_df["capacity_mw"] > 0]
filtered_df["cap_scaled"] = np.sqrt(filtered_df["capacity_mw"])

# ─────────────────────────────────────────────
# 6. MAP
# ─────────────────────────────────────────────
if len(filtered_df) == 0:
    st.warning("No data matches the selected filters.")
else:
    fig = px.scatter_geo(
        filtered_df,
        lat="latitude",
        lon="longitude",
        color="primary_fuel",
        size="cap_scaled",
        size_max=18
    )

    fig.update_traces(
        text=filtered_df["name"],
        customdata=filtered_df[["country_long", "primary_fuel"]],
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Country: %{customdata[0]}<br>"
            "Fuel: %{customdata[1]}<br>"
            "Latitude: %{lat:.3f}<br>"
            "Longitude: %{lon:.3f}<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        geo=dict(showland=True, landcolor="rgb(240,240,240)"),
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# 7. STATS
# ─────────────────────────────────────────────
st.subheader("Power Plant Statistics")

if no_filter_selected:
    filtered_count = 0
else:
    filtered_count = len(filtered_df)

percentage = (filtered_count / total_plants * 100) if total_plants > 0 else 0

col1, col2, col3 = st.columns(3)

col1.metric("Total Plants", total_plants)
col2.metric("Matching Plants", filtered_count)
col3.metric("Percentage (%)", f"{percentage:.2f}")
