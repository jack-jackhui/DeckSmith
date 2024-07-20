from pptx import Presentation

def list_layouts(template_path):
    prs = Presentation(template_path)
    for i, layout in enumerate(prs.slide_layouts):
        print(f"Layout {i}: {layout.name}")

# Example usage
template_path = "slide_template/template-1.pptx"
list_layouts(template_path)