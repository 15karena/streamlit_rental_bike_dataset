import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

st.header('Analysis of Bicycle Rental Volume in 2011')

day_hour_df = pd.read_csv("day_hour.csv")

day_hour_df["dteday"] = pd.to_datetime(day_hour_df["dteday"])
day_hour_df.sort_values(by="dteday", inplace=True)
day_hour_df.reset_index(inplace=True)

day_hour_df = day_hour_df[day_hour_df['dteday'].dt.year == 2011]

min_date = day_hour_df["dteday"].min()
max_date = day_hour_df["dteday"].max()

with st.sidebar:

    # Input rentang waktu dengan date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
main_df = day_hour_df[(day_hour_df["dteday"] >= str(start_date)) & 
                (day_hour_df["dteday"] <= str(end_date))]

def create_monthly_rent_df(df):
    filtered_data = day_hour_df[day_hour_df['dteday'].dt.year == 2011]
    monthly_orders_df = filtered_data .resample(rule='M', on='dteday').agg({
        "cnt_x" : "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%B')
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "cnt_x" : "total_renting_bike"
    }, inplace=True)
    
    return monthly_orders_df

def create_rfm_df(df):
    filtered_data = day_hour_df[day_hour_df['dteday'].dt.year == 2011]
    rfm_df = filtered_data.groupby(by="instant_x", as_index=False).agg({
        "dteday": "max",      # Mengambil tanggal rental terakhir
        "cnt_x": "sum"          # Menghitung jumlah pesanan (monetary)
    })

    rfm_df.columns = ["instant", "max_order_timestamp", "frequency"]

    # Hitung Recency (hari terakhir rental)
    #last_date = filtered_data['dteday'].max()
    #filtered_data['recency'] = (last_date - filtered_data['dteday']).dt.days

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = filtered_data["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

def create_weathersit_df(df) : 
    # Grupkan data berdasarkan weathersit dan hitung jumlah total peminjaman sepeda
    by_weathersit_df = day_hour_df.groupby(by="weathersit_x").cnt_x.sum().reset_index()
    by_weathersit_df.rename(columns={"cnt_x": "total_bike_rental"}, inplace=True)  # Ubah "cnt" menjadi "cnt_x"

    # Dictionary untuk memetakan angka weathersit ke label yang sesuai
    weather_labels = {1: "Clear", 2: "Cloudy", 3: "Light Rain"}

    # Menggunakan map() untuk mengganti nilai weathersit dengan label yang sesuai
    by_weathersit_df['weathersit_label'] = by_weathersit_df['weathersit_x'].map(weather_labels)
    
    return by_weathersit_df


monthly_orders_df = create_monthly_rent_df(main_df)
rfm_df = create_rfm_df(main_df)
by_weathersit_df = create_weathersit_df(main_df)

st.subheader('Monthly Orders')

col1 = st.columns(1)

total_rent_bike = monthly_orders_df.total_renting_bike.sum()
st.metric("Total rent bike in a year", value=total_rent_bike)
    
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["dteday"],
    monthly_orders_df["total_renting_bike"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Bicycle Rental Frequency and Last Rental: RFM Parameter Analysis")

col1, col2, = st.columns(2)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average frequency", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]


# Plot untuk Recency
sns.barplot(y="recency", x="instant", data=rfm_df.sort_values(by="recency", ascending=True).head(5), hue="instant", palette=colors, ax=ax[0], legend=False)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)

# Plot untuk frequency
sns.barplot(y="frequency", x="instant", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), hue="instant", palette=colors, ax=ax[1], legend=False)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Bicycle Rental by Weather Conditions")

# plot untuk weathersit
fig, ax = plt.subplots(figsize=(10, 5))

# Menggambar plot
sns.barplot(
    y="total_bike_rental", 
    x="weathersit_label",
    data=by_weathersit_df.sort_values(by="total_bike_rental", ascending=False),
    palette="viridis",  # Ganti dengan palet warna yang diinginkan
    ax=ax
)

# Menambahkan judul
ax.set_title("Number of Customers by Weather Condition", loc="center", fontsize=15)

# Menghilangkan label sumbu
ax.set_ylabel(None)
ax.set_xlabel(None)

# Menyesuaikan ukuran label sumbu x
ax.tick_params(axis='x', labelsize=12)

# Menampilkan plot di Streamlit
st.pyplot(fig)

