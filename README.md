# DeckSmith

DeckSmith is an AI-powered slide deck generator that creates professional McKinsey/BCG/Bain-style presentations from simple descriptions. It leverages Azure OpenAI for content generation and DALL-E for image creation.

## Features

- **AI-Powered Content Generation**: Creates structured, professional slide content using Azure OpenAI
- **Image Generation**: Generates relevant images for slides using DALL-E 3
- **Document Upload**: Upload PDF or Word documents to provide context for your presentations
- **Vector Search**: Uses FAISS for intelligent document retrieval and context-aware responses
- **Multiple Templates**: Choose from different PowerPoint templates
- **Interactive Chatbot**: Ask questions about uploaded documents
- **Email Integration**: Send chat summaries via email

## Architecture

```
DeckSmith/
├── main.py                 # Streamlit application entry point
├── chatbot.py              # Conversational AI with vector search
├── slide_deck_gen_v2.py    # Slide generation with retry logic
├── image_generator.py      # DALL-E image generation
├── vector_db.py            # FAISS vector database with persistence
├── document_processing.py  # PDF/Word processing with chunking
├── validation.py           # Authentication and input sanitization
├── tools.py                # Email tools with validation
├── constants.py            # Configuration constants
├── ui.py                   # Streamlit UI components
├── utils.py                # Utility functions
└── tests/                  # Test suite
```

## Prerequisites

- Python 3.11 or higher
- Azure OpenAI API access
- Azure DALL-E API access (optional, for image generation)
- SMTP server access (optional, for email features)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/your-repo/DeckSmith.git
cd DeckSmith
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Run the application:
```bash
streamlit run main.py
```

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Access the application at `http://localhost:8502`

## Configuration

Create a `.env` file based on `.env.example`:

```env
# Azure OpenAI (Required)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
AZURE_OPENAI_MODEL_NAME=gpt-4

# Azure DALL-E (Optional)
AZURE_DALLE_API_KEY=your_dalle_key
AZURE_DALLE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DALLE_API_VERSION=2024-02-15-preview
AZURE_DALLE_DEPLOYMENT_NAME=dall-e-3

# Authentication
DJANGO_BACKEND_URL=http://localhost:8000
FRONTENDURL=http://localhost:3000
API_KEY=your_secure_api_key

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Debug
DEBUG_MODE=false
```

## Usage

### Generating a Slide Deck

1. Enter a description of your presentation topic
2. Select a template
3. Click "Generate Slide Deck"
4. Download the generated PowerPoint file

### Using the Chatbot

1. Upload PDF or Word documents
2. Ask questions about the content
3. Request email summaries if needed

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html
```

### Linting

```bash
# Run Ruff linter
ruff check .

# Run mypy type checker
mypy --ignore-missing-imports *.py

# Run Bandit security scanner
bandit -r . -x ./tests
```

### Code Quality Tools

The project uses:
- **Ruff**: Fast Python linter
- **mypy**: Static type checking
- **Bandit**: Security vulnerability scanner
- **pytest**: Testing framework

## API Reference

### Slide Generation

The slide generator creates a 12-slide presentation:

1. Front Page
2. Executive Summary (SCR framework)
3. Key Point 1
4. Key Point 2
5. Key Point 3
6. Recommendations (3 points)
7. Conclusion
8. Additional Examples (2 examples)
9. Important Data
10. Benefits
11. Risks
12. Final Conclusion

### Vector Database

Documents are chunked and stored in a FAISS index for semantic search:

- Chunk size: 1000 characters
- Chunk overlap: 200 characters
- Embedding model: all-MiniLM-L6-v2
- Search returns top 5 results

## Security

- Input sanitization for all user inputs
- Email validation with regex
- API key authentication
- No hardcoded credentials
- Debug mode controlled via environment variable

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Code Standards

- Add type hints to all functions
- Include docstrings for public functions
- Write tests for new features
- Follow existing code style

## License

MIT License - see LICENSE file for details.

## Acknowledgements

- Azure OpenAI for LLM capabilities
- Streamlit for the web framework
- FAISS for vector search
- LangChain for AI orchestration
