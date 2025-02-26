import io

import pandas as pd
import streamlit as st
from PIL import Image
from camera_input_live import camera_input_live
import numpy as np
import plotly.graph_objects as go


def bytesio_to_np_array(bytes_stream):
    image = Image.open(bytes_stream)  # Open image from BytesIO
    return np.array(image, dtype=np.uint32)  # Convert image to numpy array

if __name__ == '__main__':
    image = st.camera_input('Please take a picture of the spectrum')

    if image:
        image = bytesio_to_np_array(image)
        if "slider" not in st.session_state:
            st.session_state["slider"] = 0
        st.session_state["slider"] = st.slider('Move the below slider such that the white bar overlays your spectrum.', 0, image.shape[0]-1, st.session_state["slider"])

        red_spectrum = []
        green_spectrum = []
        blue_spectrum = []
        full_spectrum = []
        for pixel in image[st.session_state["slider"], :]:
            red_spectrum.append(pixel[0]/255)
            green_spectrum.append(pixel[1]/255)
            blue_spectrum.append(pixel[2]/255)
            full_spectrum.append(sum(pixel)/765)

        image[st.session_state["slider"], :] = [255, 255, 255]
        st.image(image)

        fig = go.Figure()


        if st.toggle("enable calibration"):

            if st.button("Reset calibration"):
                st.session_state["calibration_coefficient"] = 1
                st.session_state["calibration_offset"] = 0

            M2 = st.slider('Move the below slider such that the green bar overlays the Mercury 2 peak at 435.8 nm.', 0, image.shape[1]-1, 0)
            M3 = st.slider('Move the below slider such that the green bar overlays the Mercury 3 peak at 546.1 nm.', 0, image.shape[1]-1, 0)

            fig.add_trace(go.Scatter(x=[M2 , M2 ], y=[0, 1], mode='lines', name='Mercury 2 line (435.8 nm)',  line = dict(color='yellow', width=1)))
            fig.add_trace(go.Scatter(x=[M3, M3], y=[0, 1], mode='lines', name='Mercury 3 line (546.1 nm)',  line = dict(color='yellow', width=1)))

            if st.button("Calibrate"):
                st.session_state["calibration_coefficient"] = (546.1 - 435.8)/(M3 - M2)
                st.session_state["calibration_offset"] = 435.8 - M2 * st.session_state["calibration_coefficient"]


        if "calibration_coefficient" not in st.session_state:
            st.session_state["calibration_coefficient"] = 1

        if "calibration_offset" not in st.session_state:
            st.session_state["calibration_offset"] = 0

        spectrum_x = np.arange(len(red_spectrum))* st.session_state["calibration_coefficient"] + st.session_state["calibration_offset"]

        fig.add_trace(go.Scatter(x=spectrum_x , y=red_spectrum, mode='lines', name='Red spectrum',  line = dict(color='red', width=2)))
        fig.add_trace(go.Scatter(x=spectrum_x, y=green_spectrum, mode='lines', name='Green spectrum',  line = dict(color='green', width=2, )))
        fig.add_trace(go.Scatter(x=spectrum_x, y=blue_spectrum, mode='lines',  name='Blue spectrum', line = dict(color='blue', width=2)))
        fig.add_trace(go.Scatter(x=spectrum_x, y=full_spectrum, mode='lines',  name='Full spectrum', line = dict(color='black', width=2)))

        fig.update_layout(
            title=dict(
                text='Light Spectra calculated from above image'
            ),
            xaxis=dict(
                title=dict(
                    text='Wavelength (nm)'
                )
            ),
            yaxis=dict(
                title=dict(
                    text='Intensity'
                )
            ),
        )
        st.plotly_chart(fig)
