import streamlit as st
import pandas as pd

st.header('test file')

filepath = st.file_uploader('Please upload a valid TTX file')

if filepath:
    first_rawdata = pd.read_csv(filepath, delimiter='\t', skiprows=[0, 1, 2, 3, 4, 5, 6, 8, 9, 10])
    rawdata = first_rawdata.copy()

    st.dataframe(rawdata)
