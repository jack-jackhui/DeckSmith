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

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center;">
            <p>Created by <a href="https://jackhui.com.au" target="_blank">Jack Hui</a></p>
            <p>Follow me on:
                <p>
                <a href="https://twitter.com/realjackhui" target="_blank">
                    <img src="https://img.icons8.com/color/48/000000/twitter--v1.png" alt="Twitter" style="width: 30px; height: 30px;"/>
                </a>
                <a href="https://github.com/jack-jackhui" target="_blank">
                    <img src="https://img.icons8.com/color/48/000000/github.png" alt="Github" style="width: 30px; height: 30px;"/>
                </a>
                <a href="https://linkedin.com/in/jackhui888" target="_blank">
                    <img src="https://img.icons8.com/color/48/000000/linkedin.png" alt="LinkedIn" style="width: 30px; height: 30px;"/>
                </a>
            </p>
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    return user_input, description, uploaded_files, generate_button_pressed, template_options[selected_template]