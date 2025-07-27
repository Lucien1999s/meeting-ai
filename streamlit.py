"""AI Meeting Automation Script.

This script provides an interface for AI Automation Meeting using Streamlit. Users can input meeting parameters,
upload files, select models, and execute the program. The script utilizes functions for applying custom styles
to display content with specified colors and font sizes.

Functions:
    - `get_custom_word(content: str, color: str, size: str) -> None`:
        Applies a custom style to display specified content with a specific color and font size.

    - `get_custom_report(content: str, word_color: str, line_color: str, size: str) -> None`:
        Applies a custom style to display a report with specified content, word color, line color, and font size.

    - `st_interface() -> None`:
        Provides a Streamlit interface for AI Automation Meeting.

Example:
    >>> st_interface()

Note:
    This script should be executed as the main module to run the AI Automation Meeting interface.

"""

import os
import logging

from PIL import Image
import streamlit as st
from src.ai_meeting_generator import run


def get_custom_word(content: str, color: str, size: str):
    """
    Applies a custom style to display a specified content with a specific color and font size.

    Args:
        content (str): The text content to be displayed.
        color (str): The color in CSS format (e.g., "#RRGGBB") to be applied to the text.
        size (str): The font size in pixels to be applied to the text.

    Returns:
        None

    Example:
        >>> get_custom_word("Hello, World!", "#FF0000", "20")
    """
    st.markdown(
        f"""
    <style>
    .custom-font {{
        font-size:{size}px !important;
        color: {color};
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="custom-font">
    {content}
    </div>
    """,
        unsafe_allow_html=True,
    )


def get_custom_report(content: str, word_color: str, line_color: str, size: str):
    """
    Applies a custom style to display a report with specified content, word color, line color, and font size.

    Args:
        content (str): The text content of the report.
        word_color (str): The color in CSS format (e.g., "#RRGGBB") to be applied to the words in the report.
        line_color (str): The color in CSS format (e.g., "#RRGGBB") to be applied to the border of the report.
        size (str): The font size in pixels to be applied to the text in the report.

    Returns:
        None

    Example:
        >>> get_custom_report("Summary Report", "#0000FF", "#00FF00", "16")
    """
    st.markdown(
        f"""
    <style>
    .border {{
        font-size:{size}px !important;
        color: {word_color};
        border: 2px solid {line_color};
        padding: 10px;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="border">
    {content}
    </div>
    """,
        unsafe_allow_html=True,
    )


def st_interface():
    """
    Provides a Streamlit interface for AI Automation Meeting, allowing users to input parameters, upload files, 
    select models, and execute the program.

    Returns:
        None

    Example:
        >>> st_interface()
    """
    # Get the background image and setup background and title
    script_dir = os.path.dirname(os.path.realpath(__file__))
    image_path = os.path.join(script_dir, "image", "ai record man.jpg")
    image = Image.open(image_path)
    st.image(image, use_column_width=True)
    st.title("AI Automation Meeting")

    # User input
    meeting_name = st.text_input("Input Meeting Name")
    api_key = st.text_input("Input API Key")

    # Select upload file type
    file_type = st.selectbox(
        "Choose Meeting Transcript Type", ["Audio Transcript", "Txt Transcript"]
    )
    if file_type == "Audio Transcript":
        uploaded_file = st.file_uploader("Please upload the audio file")
        transcript_path = None
    else:
        uploaded_file = st.file_uploader("Please upload the txt file")
        file_path = None

    # If a file is uploaded, save it to a local path
    if uploaded_file is not None and file_path is not None:
        file_path = os.path.join("/tmp", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
    else:
        transcript_path = os.path.join("/tmp", uploaded_file.name)
        with open(transcript_path, "wb") as f:
            f.write(uploaded_file.getvalue())

    # Select model
    audio_model = st.selectbox(
        "Select audio_model", ["base", "tiny", "small", "medium", "api"]
    )
    text_model = st.selectbox(
        "Select text_model", ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"]
    )

    # Select whether to save transcript and display cost
    save_transcript = st.radio("Save transcript to txt file or not", [True, False])
    show_txt_cost = st.radio("Show cost on txt files or not", [True, False])

    # Input and output paths
    output_path = st.text_input("Input the output path")

    # Execute program
    if st.button("Run"):
        if api_key == "":
            st.error("You didn't input API Key!")
        else:
            try:
                report = run(
                    meeting_name=meeting_name,
                    file_path=file_path,
                    api_key=api_key,
                    audio_model=audio_model,
                    text_model=text_model,
                    output_path=output_path,
                    transcript_path=transcript_path,
                    save_transcript=save_transcript,
                    show_txt_cost=show_txt_cost,
                    logging_level=logging.INFO,
                )
                get_custom_word(
                    content="Successfully generate ai meeting report!\n",
                    color="orange",
                    size="20",
                )
                get_custom_report(
                    content=report, word_color="LightBlue", line_color="white", size="30"
                )

            except Exception as e:
                st.error(f"An error occurred during execution:{e}")
    
    # To delete the file in /tmp
    if st.button("Delete Tmp File"):
        if file_path is not None and os.path.exists(file_path):
            os.remove(file_path)
            st.success("Successfully deleted the file at /tmp.")
        if transcript_path is not None and os.path.exists(transcript_path):
            os.remove(transcript_path)
            st.success("Successfully deleted the transcript at /tmp.")


if __name__ == "__main__":
    st_interface()
