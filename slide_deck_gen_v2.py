"""Slide deck generation module using Azure OpenAI."""

import logging
import os
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from openai import APIError, RateLimitError
from PIL import Image
from pptx import Presentation
from pptx.util import Cm, Inches, Pt
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from constants import (
    DEFAULT_FONT_SIZE,
    EXAMPLES_COUNT,
    IMAGE_RIGHT_MARGIN_CM,
    IMAGE_TOP_CM,
    MAX_RETRIES,
    MAX_SLIDES,
    PIXELS_TO_CM,
    RECOMMENDATIONS_KEY_POINTS,
    RETRY_INITIAL_WAIT,
    RETRY_MAX_WAIT,
    RETRY_MULTIPLIER,
    SLIDE_HEIGHT_CM,
    SLIDE_WIDTH_CM,
    SLIDES_STRUCTURE,
    SMALL_FONT_SIZE,
)
from image_generator import generate_cover

load_dotenv()

logger = logging.getLogger(__name__)

azure_openai_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_version: Optional[str] = os.getenv("AZURE_OPENAI_API_VERSION")
azure_openai_deployment_name: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
azure_openai_model_name: Optional[str] = os.getenv("AZURE_OPENAI_MODEL_NAME")

llm = AzureChatOpenAI(
    api_key=azure_openai_api_key,
    azure_endpoint=azure_openai_endpoint,
    api_version=azure_openai_api_version,
    deployment_name=azure_openai_deployment_name,
    model_name=azure_openai_model_name
)

LAYOUT_MAPPING = {
    "title": 0,
    "section_header": 1,
    "title_and_body": 2,
    "title_and_two_columns": 3,
    "title_only": 4,
    "one_column_text": 5,
    "main_point": 6,
    "section_title_and_description": 7,
    "caption_only": 8,
    "big_number": 9,
    "blank": 10
}


def remove_unwanted_slides(prs: Presentation, indices_to_remove: List[int]) -> Presentation:
    """Remove slides at specified indices from the presentation.

    Args:
        prs: The PowerPoint presentation object.
        indices_to_remove: List of slide indices to remove.

    Returns:
        The modified presentation object.
    """
    indices_to_remove = sorted(indices_to_remove, reverse=True)

    for index in indices_to_remove:
        slide_id = prs.slides._sldIdLst[index].rId
        prs.part.drop_rel(slide_id)
        del prs.slides._sldIdLst[index]

    return prs


def clear_existing_slides(prs: Presentation, last_index_to_clear: int) -> None:
    """Clear all slides from the presentation.

    Args:
        prs: The PowerPoint presentation object.
        last_index_to_clear: Unused parameter, kept for compatibility.
    """
    while len(prs.slides) > 0:
        xml_slides = prs.slides._sldIdLst
        prs.part.drop_rel(xml_slides[0].rId)
        del xml_slides[0]


@retry(
    retry=retry_if_exception_type((RateLimitError, APIError)),
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_INITIAL_WAIT, max=RETRY_MAX_WAIT),
    before_sleep=lambda retry_state: logger.warning(
        "Retrying LLM call (attempt %d/%d) after error: %s",
        retry_state.attempt_number, MAX_RETRIES, retry_state.outcome.exception()
    )
)
def invoke_llm(prompt: str) -> str:
    """Invoke the LLM with retry logic for rate limiting and API errors.

    Args:
        prompt: The prompt to send to the LLM.

    Returns:
        The LLM response content.

    Raises:
        RateLimitError: If rate limit is exceeded after all retries.
        APIError: If an API error occurs after all retries.
    """
    logger.debug("Invoking LLM with prompt length: %d", len(prompt))
    response = llm.invoke(prompt)
    return response.content.strip()


def generate_slide_content(description: str) -> List[str]:
    """Generate content for all slides based on the description.

    Args:
        description: The presentation description/topic.

    Returns:
        A list of content strings, one for each slide.

    Raises:
        ValueError: If generated content doesn't match expected slide count.
    """
    prompt = (
        f"You are an expert in creating professional presentations in the style of McKinsey, BCG, or Bain (MBB). "
        f"Generate concise, impactful content for a PowerPoint presentation based on the following description:\n\n"
        f"{description}\n\n"
        "Structure the content for the following slides. Each slide's content should be separated by the marker '[SLIDE]'.\n"
        "Do not use any markdown or special formatting syntax in the content.\n"
        "Do not repeat the slide titles in the body text for any slides.\n"
        "1. Front Page: Include a concise title (the description), and a catchy sub-headline.\n"
        "2. Executive Summary: Provide a brief summary using the Situation-Complication-Resolution framework, presenting the initial context (Situation), the specific challenge (Complication), and the proposed solution (Resolution).\n"
        "3. Key Point 1: This slide presents key point 1 contains two main parts:an concise Action Title that articulates the key takeaway or main message whic capture the audience's attention, explain the page's importance, and show its contribution to the storyline; Slide Body that allocated to content and exhibits that support the action title or headlines. These exhibits can take the form of graphs, tables, text, maps, or other forms of data visualization. The focus should be on presenting value-adding insights and synthesizing information.\n"
        "4. Key Point 2: This slide presents key point 2 contains two main parts:an concise Action Title that articulates the key takeaway or main message whic capture the audience's attention, explain the page's importance, and show its contribution to the storyline; Slide Body that allocated to content and exhibits that support the action title or headlines. These exhibits can take the form of graphs, tables, text, maps, or other forms of data visualization. The focus should be on presenting value-adding insights and synthesizing information.\n"
        "5. Key Point 3: This slide presents key point 3 contains two main parts:an concise Action Title that articulates the key takeaway or main message whic capture the audience's attention, explain the page's importance, and show its contribution to the storyline; Slide Body that allocated to content and exhibits that support the action title or headlines. These exhibits can take the form of graphs, tables, text, maps, or other forms of data visualization. The focus should be on presenting value-adding insights and synthesizing information.\n"
        "6. Recommendations: Provide concise recommendations in the form of three key points, each with a heading and body text. The headings should be impactful and the body text should provide clear, actionable recommendations. Separate each key point with a double newline. Do not include any exhibits or images. Do not include the word recommendation in each point.\n"
        "7. Conclusion: Summarize key points, recommendations, and actions required concisely.\n"
        "8. Additional Examples: Provide two concise examples, each with a heading and body text. Separate each example with a double newline. Do not include any exhibits or images.\n"
        "9. Important Data: Highlight important data or statistics concisely with action titles and subheadings.\n"
        "10. Benefits: Emphasize benefits concisely with action titles and subheadings.\n"
        "11. Risks: Outline potential risks and mitigation strategies concisely with action titles and subheadings.\n"
        "12. Final Conclusion: Provide a final conclusion and call to action concisely with action titles and subheadings.\n"
        "Ensure the content is engaging, informative, and suitable for a professional audience. "
        "Include relevant details and examples. Keep the content concise and within the size of the slide. "
        "Do not write any comments other than actual contents of the slide."
    )

    content = invoke_llm(prompt)
    logger.debug("Generated Content:\n%s\n", content)

    slides_content = content.split("[SLIDE]")
    for index, slide in enumerate(slides_content):
        logger.debug("Content for Slide %d:\n%s\n", index + 1, slide)
    slides_content = [slide.strip() for slide in slides_content if slide.strip()]

    logger.info("Number of slides content generated: %d", len(slides_content))
    logger.info("Expected number of slides: %d", len(SLIDES_STRUCTURE))

    if len(slides_content) != len(SLIDES_STRUCTURE):
        raise ValueError("Generated content does not match the number of defined slides")

    return slides_content


def adjust_slide_content(
    slide,
    title: str,
    content: str,
    resize_title: bool = True,
    resize_content: bool = True
) -> None:
    """Adjust slide content positioning and sizing.

    Args:
        slide: The PowerPoint slide object.
        title: The slide title.
        content: The slide content.
        resize_title: Whether to resize the title placeholder.
        resize_content: Whether to resize the content placeholder.
    """
    if resize_title:
        title_placeholder = slide.shapes.title
        if title_placeholder:
            title_placeholder.top = Inches(1.5)
            title_placeholder.width = Inches(10)
            title_placeholder.height = Inches(1.5)

    if resize_content:
        content_placeholder = None
        for shape in slide.placeholders:
            if shape.placeholder_format.idx == 1:
                content_placeholder = shape
                break
        if content_placeholder:
            content_placeholder.top = Inches(1.5)
            content_placeholder.left = Inches(0.5)
            content_placeholder.width = Inches(9)
            content_placeholder.height = Inches(5.5)

    insert_content(slide, title, content, text_placeholder_idx=1)


def create_slide(prs: Presentation, layout_name: str):
    """Create a new slide with the specified layout.

    Args:
        prs: The PowerPoint presentation object.
        layout_name: The name of the layout to use.

    Returns:
        The new slide object.

    Raises:
        ValueError: If layout name is not found.
    """
    layout_index = LAYOUT_MAPPING.get(layout_name)
    if layout_index is None:
        raise ValueError(f"No layout found for {layout_name}")
    slide_layout = prs.slide_layouts[layout_index]
    return prs.slides.add_slide(slide_layout)


def insert_content(
    slide,
    title: str,
    content: str,
    text_placeholder_idx: int,
    font_size: int = DEFAULT_FONT_SIZE,
    enlarge_text_box: bool = False,
    image_slide: bool = False,
    move_title_up: bool = False
) -> None:
    """Insert title and content into a slide.

    Args:
        slide: The PowerPoint slide object.
        title: The slide title.
        content: The slide content.
        text_placeholder_idx: Index of the text placeholder.
        font_size: Font size in points.
        enlarge_text_box: Whether to enlarge the text box.
        image_slide: Whether this is a slide with an image.
        move_title_up: Whether to move the title up.
    """
    try:
        title_placeholder = slide.shapes.title
        if title_placeholder:
            title_placeholder.text = title
            if move_title_up:
                title_placeholder.top = Inches(0.5)
    except AttributeError:
        logger.warning("No title placeholder found. Skipping title.")

    try:
        content_placeholder = None
        for shape in slide.placeholders:
            if shape.placeholder_format.idx == text_placeholder_idx:
                content_placeholder = shape
                break

        if content_placeholder:
            text_frame = content_placeholder.text_frame
            text_frame.clear()

            for paragraph in content.split('\n'):
                p = text_frame.add_paragraph()
                p.text = paragraph
                p.font.size = Pt(font_size)

            if image_slide:
                content_placeholder.width = Inches(4.5)
        else:
            logger.warning(
                "No content placeholder found for text insertion with index %d.",
                text_placeholder_idx
            )
    except Exception as e:
        logger.error("Error setting text: %s", e)


def add_image_to_slide(slide, image_path: str) -> None:
    """Add an image to a slide positioned on the right side.

    Args:
        slide: The PowerPoint slide object.
        image_path: Path to the image file.
    """
    try:
        image = Image.open(image_path)
        image_width, image_height = image.size

        image_width_cm = image_width * PIXELS_TO_CM
        image_height_cm = image_height * PIXELS_TO_CM

        while image_width_cm > SLIDE_WIDTH_CM / 3 or image_height_cm > SLIDE_HEIGHT_CM:
            image_width_cm *= 0.5
            image_height_cm *= 0.5

        top = Cm(IMAGE_TOP_CM)
        left = Cm(SLIDE_WIDTH_CM - image_width_cm - IMAGE_RIGHT_MARGIN_CM)
        height = Cm(image_height_cm)
        width = Cm(image_width_cm)

        slide.shapes.add_picture(image_path, left=left, top=top, width=width, height=height)
    except Exception as e:
        logger.error("Error adding image to slide: %s", e)


@retry(
    retry=retry_if_exception_type((RateLimitError, APIError)),
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_INITIAL_WAIT, max=RETRY_MAX_WAIT),
    before_sleep=lambda retry_state: logger.warning(
        "Retrying slide 6 regeneration (attempt %d/%d)",
        retry_state.attempt_number, MAX_RETRIES
    )
)
def regenerate_slide_6_content(description: str, max_retries: int = MAX_RETRIES) -> str:
    """Regenerate content for slide 6 (Recommendations) if initial generation failed.

    Args:
        description: The presentation description.
        max_retries: Maximum number of regeneration attempts.

    Returns:
        The regenerated content for slide 6.

    Raises:
        ValueError: If content cannot be regenerated with exactly 3 key points.
    """
    for attempt in range(max_retries):
        prompt = (
            f"You are an expert in creating professional presentations in the style of McKinsey, BCG, or Bain (MBB). "
            f"Generate concise, impactful content for the 'Recommendations' slide based on the following description:\n\n"
            f"{description}\n\n"
            "Provide concise recommendations in the form of three key points, each with a heading and body text. "
            "The headings should be impactful and the body text should provide clear, actionable recommendations. "
            "Separate each key point with a double newline. Do not include any exhibits or images. "
            "Do not include the word recommendation in each point."
        )

        content = invoke_llm(prompt)

        key_points = content.split('\n\n')
        if len(key_points) == RECOMMENDATIONS_KEY_POINTS:
            return content
        else:
            logger.warning("Regeneration attempt %d failed. Retrying...", attempt + 1)

    raise ValueError(
        f"Regenerated content for slide 6 does not contain exactly {RECOMMENDATIONS_KEY_POINTS} "
        "key points after multiple attempts"
    )


def generate_and_save_presentation(
    description: str,
    template_path: str,
    output_path: str
) -> None:
    """Generate a complete presentation and save it to a file.

    Args:
        description: The presentation description/topic.
        template_path: Path to the PowerPoint template file.
        output_path: Path where the generated presentation should be saved.

    Raises:
        ValueError: If template doesn't have enough slides or content generation fails.
    """
    try:
        slide_content = generate_slide_content(description)
        key_points = slide_content[5].split('\n\n')
        if len(key_points) != RECOMMENDATIONS_KEY_POINTS:
            raise ValueError(
                f"Generated content for slide 6 does not contain exactly "
                f"{RECOMMENDATIONS_KEY_POINTS} key points"
            )
    except ValueError as e:
        if "slide 6 does not contain exactly" in str(e):
            logger.warning("Error in generating content for slide 6. Regenerating...")
            try:
                slide_6_content = regenerate_slide_6_content(description)
                slide_content[5] = slide_6_content
            except ValueError as regen_error:
                logger.error(str(regen_error))
                raise
        else:
            raise

    prs = Presentation(template_path)

    if len(prs.slides) < len(SLIDES_STRUCTURE):
        raise ValueError("The template does not contain enough slides to match the structure")

    slides_with_images: List[int] = []
    slides_to_move_title_up: List[int] = []

    template_type = "template-2" if "template-2" in template_path else "template-1"

    for i, slide in enumerate(prs.slides):
        if i < len(SLIDES_STRUCTURE):
            title = description if i == 0 else SLIDES_STRUCTURE[i]["title"]
            content = slide_content[i]

            if i == 5:  # Recommendations slide
                key_points = content.split('\n\n')

                if template_type == "template-2":
                    body_indices = [1, 2, 3]
                    heading_indices = [4, 5, 6]
                else:
                    heading_indices = [4, 6, 8]
                    body_indices = [3, 5, 7]

                for j, key_point in enumerate(key_points):
                    if '\n' in key_point:
                        heading, body = key_point.split('\n', 1)
                    else:
                        heading = key_point
                        body = ""
                    insert_content(
                        slide, title, heading,
                        text_placeholder_idx=heading_indices[j],
                        font_size=DEFAULT_FONT_SIZE,
                        enlarge_text_box=False
                    )
                    insert_content(
                        slide, title, body,
                        text_placeholder_idx=body_indices[j],
                        font_size=SMALL_FONT_SIZE,
                        enlarge_text_box=True
                    )
            elif i == 7:  # Examples slide
                examples = content.split('\n\n')
                if len(examples) != EXAMPLES_COUNT:
                    raise ValueError(
                        f"Generated content for slide 8 does not contain exactly "
                        f"{EXAMPLES_COUNT} examples"
                    )
                if template_type == "template-2":
                    heading_indices = [3, 4]
                    body_indices = [1, 2]
                else:
                    heading_indices = [2, 4]
                    body_indices = [1, 3]

                for j, example in enumerate(examples):
                    if '\n' in example:
                        heading, body = example.split('\n', 1)
                    else:
                        heading = example
                        body = ""
                    insert_content(
                        slide, title, heading,
                        text_placeholder_idx=heading_indices[j],
                        font_size=DEFAULT_FONT_SIZE,
                        enlarge_text_box=False
                    )
                    insert_content(
                        slide, title, body,
                        text_placeholder_idx=body_indices[j],
                        font_size=SMALL_FONT_SIZE,
                        enlarge_text_box=True
                    )
            elif i in [8, 9, 10]:  # Data, Benefits, Risks slides
                title_placeholder = slide.shapes.title
                if title_placeholder:
                    title_placeholder.text = SLIDES_STRUCTURE[i]["title"]
                for shape in slide.placeholders:
                    if shape.placeholder_format.idx != title_placeholder.placeholder_format.idx:
                        shape.text = ""
                insert_content(
                    slide, SLIDES_STRUCTURE[i]["title"], content,
                    text_placeholder_idx=1,
                    font_size=DEFAULT_FONT_SIZE,
                    enlarge_text_box=True
                )
            else:
                if template_type == "template-2":
                    text_placeholder_idx = 1
                else:
                    if i in [0, 8, 9, 10]:
                        text_placeholder_idx = 1
                    else:
                        text_placeholder_idx = 3
                move_title_up = i in slides_to_move_title_up

                if i in slides_with_images:
                    insert_content(
                        slide, title, content, text_placeholder_idx,
                        image_slide=True, move_title_up=move_title_up
                    )
                    module = {"topic": title, "key_points": content.split('\n')}
                    module = generate_cover(i, module)
                    if module["filename"]:
                        add_image_to_slide(slide, module["filename"])
                else:
                    insert_content(
                        slide, title, content, text_placeholder_idx,
                        enlarge_text_box=True, move_title_up=move_title_up
                    )

        logger.info("Inserted content for slide %d", i + 1)

    indices_to_remove = list(range(MAX_SLIDES, len(prs.slides)))
    prs = remove_unwanted_slides(prs, indices_to_remove)
    prs.save(output_path)
    logger.info("Presentation saved to %s", output_path)
