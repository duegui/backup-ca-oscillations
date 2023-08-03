@st.cache_data
def rawdata(filepath):

    # Importing raw data
    rawdata = pd.read_csv(filepath, delimiter='\t', skiprows=[0, 1, 2, 3, 4, 5, 6, 8, 9, 10])

    rawdata = rawdata.drop(['Unnamed: 0'], axis=1)

    rawdata['Time[min]'] = rawdata['No.'] / 1000 * (1 / 60)

    rawdata.rename(columns={'No.': 'Time[ms]'}, inplace=True)

    list_of_wells = list(rawdata)[1:-1]

    return rawdata, list_of_wells