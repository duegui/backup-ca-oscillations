import streamlit as st
import all_functions as af
from PIL import Image

st.set_page_config(page_title="Calcium oscillations analysis tool", layout="wide")

st.sidebar.subheader('File upload')
number_of_wells = st.sidebar.radio("Plate size", [96, 384], disabled=True, horizontal=True)
st.sidebar.caption('Currently, analysis is only possible on 96-well plates')
st.sidebar.write('\n')
filepath = st.sidebar.file_uploader('Please upload a valid TTX file')

# The app works only when a valid data file has been uploaded. Otherwise, a message comes indicating
# how to upload a valid TXT file.
if filepath is None:
    st.title('To start, select a valid TXT file')
    st.subheader(
        "To export a valid TXT file from the FDSS Hamamatsu software, make sure to comply with the following settings:")

    image = Image.open('settings.png')
    st.image(image)
    st.sidebar.write('\n')
    st.sidebar.write('\n')
    st.sidebar.subheader("Clear all Cache Data before analysing a new file")
    if st.sidebar.button("Clear All Cache Data"):
        # Clear values from *all* all in-memory and on-disk data caches:
        st.cache_data.clear()
        st.sidebar.write('Cache has been cleared')

else:
    # Selecting parameters
    if number_of_wells == 96:
        nrcolumns = 98
    else:
        nrcolumns = 386
    # nrcolumns will be main factor defining the behaviour of the app. Data will be visualized different
    # for 384 well plates. This is a new test.

    summary_metadata, rawdata = af.importing(filepath, nrcolumns)
    st.sidebar.dataframe(summary_metadata)

    st.sidebar.subheader('Defining analysis settings')
    threshold = st.sidebar.slider("Select a global detection threshold", min_value=0.01, max_value=0.1, value=0.02,
                                  help='Recommended value 0.02', step=0.005, format="%f")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Summary of all data", "Display individual well", "Configure plate conditions",
                                            "Configure statistical tests", "Export summary of analysis"])
    with tab1:
        af.all_plotting(rawdata, threshold, number_of_wells)
        if st.checkbox("Display rawdata"):
            st.dataframe(data=rawdata['rawdata'])

    with tab2:
        analysiswell = st.selectbox('Type or select well to plot and analyze', rawdata['wells'])
        st.subheader('Plotting well ' + analysiswell)
        af.well_plot(analysiswell, rawdata, threshold, summary_metadata)


    with tab3:
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

        if st.button('Add condition layer'):
            af.add_condition_layer(selection)

    with tab4:
        st.subheader('Defined layers')
