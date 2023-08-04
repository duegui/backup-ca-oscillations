import streamlit as st
import pandas as pd
import all_functions as af
from PIL import Image


st.set_page_config(page_title="Calcium oscillations analysis tool", layout="wide")

st.sidebar.subheader('File upload')
filepath = st.sidebar.file_uploader('Please upload a valid TTX file')

if filepath is not None:
    nrcolumns = 98
    column_names = [i for i in range(nrcolumns)]

    alldata = pd.read_csv(filepath, header=None, delimiter='\t', names=column_names)

   # Metadata
    summary_metadata = {'File_name': (alldata.iloc[0, 2]).split("\\")[-1], 'Data_type': alldata.iloc[8, 2],
                        'Acquisition_date': pd.to_datetime(alldata.iloc[2, 2]),
                        'Acquisition_time': pd.to_timedelta(alldata.iloc[3, 2]),
                        'Marker': pd.to_timedelta(alldata.iloc[5, 2])}
    summary_metadata['Marker_int'] = summary_metadata['Marker'] / pd.Timedelta(minutes=1)



    # Rawdata
    df = alldata.drop([0, 1, 2, 3, 4, 5, 7, 8, 9])
    del df[df.columns[0]]
    columns_header = list(df.iloc[0])
    prerawdata = pd.DataFrame(df.values[1:], columns=columns_header)

    rawdata = prerawdata.astype(float)
    rawdata = prerawdata.astype(float)
    rawdata['Time[min]'] = rawdata['No.'] / 1000 * (1 / 60)
    rawdata.rename(columns={'No.': 'Time[ms]'}, inplace=True)
    list_of_wells = list(rawdata)[1:-1]

    rawdata_dict = {"rawdata": rawdata, "wells": list_of_wells}

    #
    # rawdata_dict = {"rawdata": rawdata, "wells": list_of_wells}
    #
    #
    st.dataframe(rawdata)
    # st.dataframe(rawdata_dict['rawdata'])


