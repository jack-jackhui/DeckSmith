"""Constants and configuration values for DeckSmith."""

from typing import Dict, List

# =============================================================================
# Slide Generation Constants
# =============================================================================
SLIDES_STRUCTURE: List[Dict[str, str]] = [
    {"title": "Front Page"},
    {"title": "Executive Summary"},
    {"title": "Key Point 1"},
    {"title": "Key Point 2"},
    {"title": "Key Point 3"},
    {"title": "Recommendations"},
    {"title": "Conclusion"},
    {"title": "Additional Examples"},
    {"title": "Important Data"},
    {"title": "Benefits"},
    {"title": "Risks"},
    {"title": "Final Conclusion"}
]

LAYOUT_MAPPING: Dict[str, int] = {
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

# Number of key points expected in recommendations slide
RECOMMENDATIONS_KEY_POINTS: int = 3

# Number of examples expected in examples slide
EXAMPLES_COUNT: int = 2

# Maximum slides to keep (remove any after this index)
MAX_SLIDES: int = 12

# =============================================================================
# Font and Layout Constants
# =============================================================================
DEFAULT_FONT_SIZE: int = 10
SMALL_FONT_SIZE: int = 9
CONTENT_FONT_SIZE: int = 16

# Inches
TITLE_TOP_POSITION: float = 1.5
TITLE_WIDTH: float = 10
TITLE_HEIGHT: float = 1.5
CONTENT_TOP_POSITION: float = 1.5
CONTENT_LEFT_MARGIN: float = 0.5
CONTENT_WIDTH: float = 9
CONTENT_HEIGHT: float = 5.5
IMAGE_COLUMN_WIDTH: float = 4.5
TITLE_MOVED_UP_POSITION: float = 0.5

# Centimeters (for image positioning)
SLIDE_WIDTH_CM: float = 24.4
SLIDE_HEIGHT_CM: float = 19.05
IMAGE_TOP_CM: float = 2.0
IMAGE_RIGHT_MARGIN_CM: float = 1.0
IMAGE_MAX_WIDTH_RATIO: float = 1/3

# =============================================================================
# Image Generation Constants
# =============================================================================
IMAGE_SIZE_LANDSCAPE: str = "1792x1024"
IMAGE_SIZE_PORTRAIT: str = "1024x1792"
IMAGE_QUALITY: str = "standard"
IMAGE_DOWNLOAD_TIMEOUT: int = 30

# Pixels to cm conversion factor
PIXELS_TO_CM: float = 0.0264583333

# =============================================================================
# API and Network Constants
# =============================================================================
REQUEST_TIMEOUT: int = 30
LLM_REQUEST_TIMEOUT: int = 120

# Retry configuration
MAX_RETRIES: int = 3
RETRY_INITIAL_WAIT: float = 1.0
RETRY_MAX_WAIT: float = 60.0
RETRY_MULTIPLIER: float = 2.0

# =============================================================================
# Vector DB Constants
# =============================================================================
EMBEDDING_DIMENSION: int = 384
EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
VECTOR_SEARCH_TOP_K: int = 5
FAISS_INDEX_FILENAME: str = "faiss_index.bin"
TEXTS_FILENAME: str = "texts.pkl"
DEFAULT_DATA_DIR: str = "data"

# =============================================================================
# Document Processing Constants
# =============================================================================
MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB
MAX_FILE_SIZE_MB: int = 10
CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 200

# =============================================================================
# Email Constants
# =============================================================================
EMAIL_SUBJECT_MAX_LENGTH: int = 255
EMAIL_TIMEOUT: int = 30

# =============================================================================
# UI Constants
# =============================================================================
TYPING_SPEED: float = 0.01  # seconds per character
FILENAME_MAX_LENGTH: int = 50
