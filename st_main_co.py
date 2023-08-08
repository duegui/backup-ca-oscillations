# This is the main Streamlit file. This file is the deployed to the Streamlit server, from Git.
# It contains main Streamlit functionality. Defines the widgets and the instructions to follow.
# It is linked to all_functions, where the different functions are defined.

import streamlit as st
import all_functions as af
from PIL import Image
import pandas as pd
from copy import deepcopy
import time

st.set_page_config(page_title="Calcium oscillations analysis tool", layout="wide")
st.title("Calcium oscillations analysis tool for FDSS files")

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(["File info", "Global configuration", "Manual configuration",
                                              "Configure plate conditions", "Configure statistical tests",
                                              "Analysis"])
# These widgets are always present in the app.
with tab0:
    with st.expander("File uploader", expanded=False):
        number_of_wells = st.radio("Plate size", [96, 384], disabled=True, horizontal=True)
        st.caption('Currently, the analysis is only enabled for 96-well plates')
        st.write('\n')
        filepath = st.file_uploader('Please upload a valid TTX file', type='TXT', help='To export a valid TXT file from the Hamamatsu FDSS software'
                                                                                       'please follow the instructions described in the picture below')
        if not filepath:
            if st.button("Clear all Cache Data before analyzing a new file"):
                # Clear values from *all* all in-memory and on-disk data caches:
                st.cache_data.clear()
                st.write('Cache has been cleared')
            st.write('\n')
            st.write('\n')
            image = Image.open('settings.jpg')
            st.image(image)


# The variable nrcolumns will be main factor defining the behaviour of the app. Data will be visualized different
# for 384 well plates.

#Sidebar
if filepath:
    if number_of_wells == 96:
        nr_columns = 98
    else:
        nr_columns = 386
    summary_metadata, rawdata = af.importing(filepath, nr_columns)


    # # Configuring sidebar
    # @st.cache_data #a loader... just deco, probably useless
    # def loadingpf():
    #     with st.sidebar.empty():
    #         for seconds in range(5):
    #             st.write(f"⏳ Please, wait while your file is being uploaded...")
    #             time.sleep(1)
    #         st.write(f"✔️{summary_metadata['File_name']} is ready!")
    # loadingpf()


    st.sidebar.subheader('Define analysis settings')
    threshold = st.sidebar.slider("Select a global detection threshold", min_value=0.01, max_value=0.1, value=0.02,
                                  help='Recommended value 0.02', step=0.005, format="%f")

    # DEFINING MAIN DICTIONARY FOR ANALYSIS RESULTS PER WELL
    analysis_dict = dict.fromkeys(rawdata['wells'], None)

    for key in analysis_dict:
        analysis_dict[key] = {'Threshold': threshold}


    manualwells = af.custom_wells(rawdata)



    with tab1:
        if number_of_wells == 96:
            af.all_plotting96(rawdata, analysis_dict)

        else:
            tab1a, tab2a, tab3a, tab4a = st.tabs(["Group 1", "Group 2", "Group 3", "Group 4"])
            af.all_plotting384(rawdata, threshold)

    with tab0:
        if filepath:
            st.subheader('File info')
            "File name: " + summary_metadata['File_name']
            "Data type: " + summary_metadata['Data_type']
            "Acquisition date and time: " + summary_metadata['Acquisition_date'].strftime('%B %d, %Y') + " at " + summary_metadata['Acquisition_time'].strftime('%H:%M') + " h."
            if st.checkbox('Show full dataset'):
                st.dataframe(data=rawdata['rawdata'])
            else:
                st.dataframe(data=rawdata['rawdata'].head())
            st.write('\n')


    with tab2:

        analysiswell = st.selectbox('Select well for manual threshold configuration', manualwells)

        if analysiswell:
            st.subheader('Plotting well ' + analysiswell)

            specific_threshold = st.slider("Select a specific detection threshold for "+analysiswell,
                                                                         min_value=0.01, max_value=0.1, value=0.02,
                                                                         help='Recommended value 0.02', step=0.005, format="%f")
            analysis_dict[analysiswell]['Threshold'] = specific_threshold
            st.dataframe(analysis_dict)
            af.well_plot(analysiswell, rawdata, analysis_dict[analysiswell]['Threshold'], summary_metadata)


    with tab3:
        st.write(summary_metadata['File_name'])
        st.subheader('Specifying wells to compare')
        st.caption("For proping copy/paste functions, prevent Microsoft Edge from blocking Streamlit (click on the right popup dialog within the URL line above)")

        if number_of_wells == 96:
            rows = 8
            columns = 12
            df = af.template(rows, columns)
            selection = st.data_editor(df)

        else:
            rows = 16
            columns = 24
            df = af.template(rows, columns)
            selection = st.data_editor(df, height=610)

        #todo define condition layers
        if st.text_input('Define a tag and add condition layer'):
            af.add_condition_layer(selection)


    with tab4:
        st.write(summary_metadata['File_name'])
        st.subheader('Defined layers')


    with tab5:
        st.write(summary_metadata['File_name'])
        st.subheader('Defined layers')
