import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import scipy as sp

@st.cache_data
def importing(filepath, nrcolumns):
    # Generate column names
    column_names = [i for i in range(nrcolumns)]

    alldata = pd.read_csv(filepath, header=None, delimiter='\t', names=column_names)

    # Metadata
    summary_metadata = {'File_name': (alldata.iloc[0, 2]).split("\\")[-1], 'Data_type': alldata.iloc[8, 2],
                        'Acquisition_date': pd.to_datetime(alldata.iloc[2, 2]),
                        'Acquisition_time': pd.to_datetime(alldata.iloc[3, 2]),
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

    return summary_metadata, rawdata_dict
@st.cache_data(experimental_allow_widgets=True)
def all_plotting96(rawdata, analysis_dict):

    with st.spinner('Plotting your data. This might take up to 5 seconds...'):

        from plotly.subplots import make_subplots
        wells = rawdata['wells']

        rows = 8
        cols = 12


        fig = make_subplots(rows, cols, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=wells)

        i, j = 1, 1
        for well in wells:
            fig.add_trace(go.Scatter(x=rawdata['rawdata']['Time[min]'], y=rawdata['rawdata'][well], showlegend=False, name=well,
                                     marker=dict(color='#3366CC')), row=j, col=i)

            x = rawdata['rawdata']['Time[min]']
            y = rawdata['rawdata'][well]

            from scipy.signal import find_peaks

            X = np.array(x.to_numpy())
            Y = np.array(y.to_numpy())

            if analysis_dict[well]['Local threshold'] == None:
                prominence_ = analysis_dict[well]['Global threshold']
            else:
                prominence_ = analysis_dict[well]['Local threshold']

            peaks, properties = find_peaks(Y, prominence=prominence_)

            fig.add_trace(go.Scatter(mode='markers', x=x[peaks], y=Y[peaks], showlegend=False,
                                     marker=dict(size=5, color='#EF553B', symbol='triangle-down')), row=j, col=i)

            i += 1
            if i == 13:
                i = 1
                j += 1

        if st.sidebar.checkbox("Zoom onto main plots for examination"):
            fig.update_layout(height=4000, width=7000)
        else:
            fig.update_layout(height=700, width=1200)

        st.plotly_chart(fig)
    return fig


#all_plotting384
# @st.cache_data(experimental_allow_widgets=True)
# def all_plotting384(rawdata, threshold):
#
#     #todo configure for 384
#
#     with st.spinner('Plotting your data. This might take up to 20 seconds...'):
#
#         from plotly.subplots import make_subplots
#         wells = rawdata['wells']
#         rows = 16
#         cols = 24
#
#
#         fig = make_subplots(rows, cols, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=wells)
#
#         i, j = 1, 1
#         for well in wells:
#             fig.add_trace(go.Scatter(x=rawdata['rawdata']['Time[min]'], y=rawdata['rawdata'][well], showlegend=False, name=well,
#                                      marker=dict(color='#3366CC')), row=j, col=i)
#
#             x = rawdata['rawdata']['Time[min]']
#             y = rawdata['rawdata'][well]
#
#             from scipy.signal import find_peaks
#
#             X = np.array(x.to_numpy())
#             Y = np.array(y.to_numpy())
#
#             peaks, properties = find_peaks(Y, prominence=threshold)
#
#             fig.add_trace(go.Scatter(mode='markers', x=x[peaks], y=Y[peaks], showlegend=False,
#                                      marker=dict(size=5, color='#EF553B', symbol='triangle-down')), row=j, col=i)
#
#             i += 1
#             if i == 13:
#                 i = 1
#                 j += 1
#
#         if st.sidebar.checkbox("Zoom"):
#             fig.update_layout(height=4000, width=7000)
#         else:
#             fig.update_layout(height=700, width=1200)
#
#         st.plotly_chart(fig)
#     return fig
@st.cache_data
def well_plot(analysiswell, rawdata, threshold, summary_metadata):

#todo change well_plot to provide only flag wells
    x = rawdata['rawdata']['Time[min]']
    y = rawdata['rawdata'][analysiswell]

    fig2 = px.line(rawdata['rawdata'], x, y, width=1300, height=700,
                   labels={"Time[min]_int": "Time (minutes)", analysiswell: "Ratio"})
    fig2.update_xaxes(rangeslider_visible=True)
    fig2.add_vline(x=summary_metadata['Marker_int'], line_width=3, line_dash="dash", line_color="green")

    #creating numpy arrays for trace analysis
    npx= np.array(x.to_numpy())
    npy = np.array(y.to_numpy())
    npy_threshold = npy+(threshold-0.01)

    peaks, properties = sp.signal.find_peaks(npy, prominence=threshold)

    fig2.add_trace(go.Scatter(mode='markers', x=npx[peaks], y=npy[peaks],
                              marker=dict(size=10, color='#EF553B', symbol='triangle-down'), name='Detected Peaks'))

    #create lowpass filter, apply, add to figure
    b, a = sp.signal.butter(3, 0.04)
    npy_threshold_filtered = sp.signal.filtfilt(b, a, npy_threshold)

    fig2.add_trace(go.Scatter(x=npx, y=npy_threshold_filtered, mode='lines',
                              name = "Current defined threshold: "+str(threshold),
                              line=go.scatter.Line(color="orange", width=2), showlegend=True))

    st.plotly_chart(fig2)

    return fig2


def template(rows,columns):
    # Creating list of letters
    list_letters = []
    start_from = ord('A')
    for i in range(rows):
        list_letters.append(chr(start_from + i))

    # Creating list of numbers
    list_numbers = []
    for i in range(columns):
        list_numbers.append(str(i+1))

    # Creating the dataframe with well names
    dict = {}
    for i in list_numbers:
        temp_list = []
        list_ones = []
        for j in list_letters:
            temp_list.append(j+i)
            list_ones.append(1)
        dict[i] = temp_list

    df = pd.DataFrame(dict)

    return df
def add_condition_layer(selection_df):
    st.toast('Layer has been added', icon='🥳')
@st.cache_data(experimental_allow_widgets=True)
def custom_wells(rawdata):
    options = st.sidebar.multiselect('Set threshold manually for the following wells:', rawdata['wells'])
    return options

