# LinkedIn Post Automation with Gemini AI

This application automates LinkedIn post creation using Google's Gemini AI for content generation and LinkedIn's API for posting. It features OAuth2 authentication, secure token management, content optimization, and post scheduling capabilities.

## Features

- 🤖 AI-powered content generation using Google's Gemini
- 🔒 Secure OAuth2 authentication with LinkedIn
- 📝 Automatic content optimization and hashtag generation
- ⏰ Post scheduling capabilities
- 📊 Post analytics tracking
- 🔐 Encrypted token storage
- 📝 Batch post creation

## Prerequisites

- Python 3.8 or higher
- LinkedIn Developer Account and API Credentials
- Google Gemini API Key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd linkedin-post-automation
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
GEMINI_API_KEY=your_gemini_key
REDIRECT_URI=http://localhost:8000/callback
```

## Usage

### Command Line Interface

1. Post about specific topics immediately:
```bash
python src/main.py --topics "AI in Healthcare" "Future of Work" "Tech Trends"
```

2. Schedule posts for a future time:
```bash
python src/main.py --topics "AI in Healthcare" --schedule "2024-03-27 15:30"
```

3. Read topics from a file:
```bash
python src/main.py --file topics.txt
```

### Python API

```python
import asyncio
from src import LinkedInPostAutomation

async def main():
    automation = LinkedInPostAutomation()
    
    # Initialize the system
    if await automation.initialize():
        topics = ["AI in Healthcare", "Future of Work"]
        await automation.create_and_post_content(topics)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Environment Variables

- `LINKEDIN_CLIENT_ID`: Your LinkedIn application client ID
- `LINKEDIN_CLIENT_SECRET`: Your LinkedIn application client secret
- `GEMINI_API_KEY`: Your Google Gemini API key
- `REDIRECT_URI`: OAuth callback URL (default: http://localhost:8000/callback)
- `DEBUG`: Enable debug logging (optional)
- `LOG_LEVEL`: Set logging level (optional)
- `TOKEN_ENCRYPTION_KEY`: Custom encryption key for token storage (optional)

### LinkedIn API Setup

1. Create a LinkedIn Developer Account
2. Create a new application
3. Add OAuth 2.0 redirect URL: http://localhost:8000/callback
4. Request the following OAuth 2.0 Scopes:
   - r_liteprofile
   - w_member_social

### Content Generation

The content generator can be customized by modifying the prompts in `content_generator.py`. Available options include:

- Tone adjustment (professional, casual, technical)
- Content length customization
- Hashtag count and style
- Industry-specific terminology

## Security

- OAuth tokens are encrypted at rest
- Sensitive credentials are stored in environment variables
- Rate limiting protection
- Automatic token refresh

## Development

### Project Structure

```
linkedin_poster/
├── .env
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── oauth_handler.py
│   ├── content_generator.py
│   ├── linkedin_manager.py
│   └── utils.py
├── tests/
├── requirements.txt
└── README.md
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.