from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
from usa_token import settings
import os
import streamlit as st
import plotly.express as px

def download_dataset():
    # Kaggle API client
    api = KaggleApi()
    
    # Autenticar utilizando token
    api.set_config_value('username', settings.kaggle_username)
    api.set_config_value('key', settings.kaggle_key)
    api.authenticate()
    
    # Definir um dataset e um caminho de onde baixar os dados
    dataset = 'piterfm/massive-missile-attacks-on-ukraine'
    path = './dados'

    # Download the dataset
    api.dataset_download_files(dataset, path=path, unzip=True)
    print(f"Dataset {dataset} baixado com sucesso!")

def process_dataset(data):
    # Drop unnecessary columns
    data.drop(columns=['time_end', 'model', 'launch_place', 'target', 'destroyed_details', 'carrier', 'source'], inplace=True)
    data['time_start'] = data['time_start'].astype(str).apply(lambda x: x.split(' ')[0])
    data.rename(columns={'time_start': 'date'}, inplace=True)
    data['date'] = pd.to_datetime(data['date']).dt.date
    return data

def monthly_interception_rate(data):
    data['date'] = pd.to_datetime(data['date'])
    monthly_data = data.resample('M', on='date').sum().reset_index()
    monthly_data['interception_rate'] = (monthly_data['destroyed'] / monthly_data['launched'] * 100).fillna(0).round(0).astype(int)
    monthly_data['interception_rate'] = monthly_data['interception_rate'].astype(str) + '%'
    monthly_data['date'] = monthly_data['date'].dt.strftime('%Y-%m')
    return monthly_data

def plot_data(data):
    fig = px.bar(data, x='date', y=['launched', 'destroyed'],
                 labels={'value': 'Count', 'variable': 'Category'},
                 barmode='group')
    fig.update_layout(
        title='Missiles Launched vs Destroyed Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Missiles'
    )
    return fig

def plot_interception_rate(data):
    fig = px.line(data, x='date', y='interception_rate')
    fig.update_layout(
        title='Monthly Average Interception Rate Over Time',
        xaxis_title='Month',
        yaxis_title='Interception Rate (%)'
    )
    return fig

root = os.getcwd()
dados_dir = f'{root}/dados'

st.title("Painel de Análise - Larissa") 

if st.sidebar.button('Download dos dados', type="primary"):
    download_dataset()

# Load and process the data
data = pd.read_csv(f"{dados_dir}/missile_attacks_daily.csv")
data_processed = process_dataset(data.copy())
st.write("Data Processed", data_processed)

# Plot and display the graphs
monthly_data = monthly_interception_rate(data_processed)
st.write("Monthly Data", monthly_data)

st.plotly_chart(plot_data(data_processed), use_container_width=True)
st.plotly_chart(plot_interception_rate(monthly_data), use_container_width=True)
