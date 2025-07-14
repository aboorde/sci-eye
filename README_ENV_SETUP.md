# Environment Setup

## API Key Configuration

This project uses environment variables to securely manage API keys.

### Setup Instructions:

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Add your OpenAI API key:**
   Open the `.env` file and replace `your_openai_api_key_here` with your actual OpenAI API key:
   ```
   OPENAI_API_KEY=sk-...your-key-here...
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the monitor:**
   ```bash
   python3 pharma_news_monitor.py
   ```

### Security Notes:
- Never commit the `.env` file to version control
- The `.gitignore` file is configured to exclude `.env`
- Keep your API keys secure and rotate them regularly
- Use different API keys for development and production