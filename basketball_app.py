import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings("ignore")

st.title('NBA Player Stats Explorer')

st.markdown("""
This app performs simple webscraping of NBA player stats data!
* Python libraries: base64, pandas, streamlit
* Data source: [Basketball-reference.com](https://www.basketball-reference.com/).
""")

st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950,2020))))

# Web scraping of NBA player stats
@st.cache_data
def load_data(year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
    html = pd.read_html(url, header=0)
    df = html[0]
    
    # # Debugging: Print column names to check if 'Tm' exists
    # st.write("Columns in the dataset:", df.columns.tolist())

    raw = df.drop(df[df.Age == 'Age'].index, errors='ignore')  
    raw = raw.fillna(0)
    playerstats = raw.drop(columns=['Rk'], errors='ignore')  # Drop 'Rk' safely
    return playerstats

playerstats = load_data(selected_year)


# Sidebar - Team selection
sorted_unique_team = sorted(playerstats.Team.astype(str).unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['C','PF','SF','PG','SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# Filtering data
df_selected_team = playerstats[(playerstats.Team.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

# Download NBA player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')

    corr = df.select_dtypes(include=[np.number]).corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        fig, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True, annot=True)
    st.pyplot(fig)
    