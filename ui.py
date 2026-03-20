"""UI components module for DeckSmith Streamlit application."""

from typing import List, Optional, Tuple

import streamlit as st


def display_ui() -> Tuple[str, str, Optional[List], bool, str]:
    """Display the main UI components for the DeckSmith application.

    Returns:
        A tuple containing:
        - user_input: The user's chat input
        - description: The slide deck description
        - uploaded_files: List of uploaded files or None
        - generate_button_pressed: Whether the generate button was clicked
        - selected_template: Path to the selected template file
    """
    st.header("Upload a PDF/Word and ask the chatbot about the contents")
    user_input: str = st.text_input("You:", "")

    st.header("Generate Slide Deck")
    description: str = st.text_area("Enter a short description for your slide deck:")

    template_folder = "slide_template"
    template_options = {
        "Template 1": f"{template_folder}/template-1.pptx",
        "Template 2": f"{template_folder}/template-2.pptx"
    }
    selected_template_name: str = st.selectbox(
        "Choose a PowerPoint template",
        list(template_options.keys())
    )

    generate_button_pressed: bool = st.button("Generate Slide Deck")

    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose PDF or Word documents",
        accept_multiple_files=True,
        type=['pdf', 'docx']
    )

    return (
        user_input,
        description,
        uploaded_files,
        generate_button_pressed,
        template_options[selected_template_name]
    )
