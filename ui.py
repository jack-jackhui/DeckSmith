import streamlit as st

def display_ui():
    st.header("Upload a PDF/Word and ask the chatbot about the contents")
    user_input = st.text_input("You:", "")

    st.header("Generate Slide Deck")
    description = st.text_area("Enter a short description for your slide deck:")

    # Add a dropdown to select a template
    template_folder = "slide_template"
    template_options = {
        "Template 1": f"{template_folder}/template-1.pptx",
        "Template 2": f"{template_folder}/template-2.pptx"
    }
    selected_template = st.selectbox("Choose a PowerPoint template", list(template_options.keys()))

    generate_button_pressed = st.button("Generate Slide Deck")

    st.header("Upload Documents")
    uploaded_files = st.file_uploader("Choose PDF or Word documents", accept_multiple_files=True, type=['pdf', 'docx'])

    return user_input, description, uploaded_files, generate_button_pressed, template_options[selected_template]