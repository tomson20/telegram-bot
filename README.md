# 🤖 AI Personal Assistant Telegram Bot

A sophisticated multilingual Telegram bot powered by Claude-3.5 Sonnet that serves as your personal AI assistant. Supports both Georgian (ქართული) and English languages with intelligent conversation memory.

## ✨ Features

### 🌍 Multilingual Support
- **Georgian (ქართული)** and **English** language support
- Automatic language detection
- Context-aware responses in the user's preferred language

### 🧠 Advanced AI Capabilities
- Powered by **Claude-3.5 Sonnet** (via Langdock API)
- Intelligent conversation memory
- Personal assistant functionality
- Context-aware responses

### 💾 Smart Memory Management
- SQLite database for conversation history
- User profiles and preferences
- Configurable context length
- Automatic cleanup of old messages

### 📊 User Analytics
- Message statistics
- User activity tracking
- Personalized experience

### 🎛️ Interactive Interface
- Inline keyboards for easy navigation
- Command shortcuts
- User-friendly interface

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Langdock API Key (free Claude access)

### 1. Get Your Tokens

#### Telegram Bot Token:
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the bot token

#### Langdock API Key:
1. Visit [Langdock.com](https://langdock.com)
2. Sign up for free account
3. Get your API key from dashboard
4. Free tier includes Claude-3.5 Sonnet access

### 2. Local Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd telegram-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your tokens
```

### 3. Configure .env File

```env
TELEGRAM_TOKEN="your_telegram_bot_token_here"
LANGDOCK_API_KEY="your_langdock_api_key_here"
ADMIN_USER_ID="your_telegram_user_id"  # Optional
```

### 4. Run Locally

```bash
python bot.py
```

## 🌐 Deployment on Railway

Railway is the recommended platform for deployment (better than Render for this use case).

### Why Railway?
- ✅ **Always-on**: No sleeping like Render
- ✅ **500 hours/month free**: Generous free tier
- ✅ **Better performance**: Faster cold starts
- ✅ **Easy deployment**: Git-based deployment
- ✅ **Built-in PostgreSQL**: If needed later

### Deploy to Railway

1. **Create Railway Account**
   - Visit [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **Create New Project on Railway**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect the Dockerfile

4. **Set Environment Variables**
   In Railway dashboard, go to Variables tab and add:
   ```
   TELEGRAM_TOKEN=your_bot_token
   LANGDOCK_API_KEY=your_langdock_key
   ADMIN_USER_ID=your_user_id
   ```

5. **Deploy**
   - Railway will automatically build and deploy
   - Your bot will be live in ~2-3 minutes

### Alternative: One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

## 🎯 Usage

### Commands
- `/start` - Initialize the bot
- `/newchat` - Clear conversation context
- `/stats` - View your statistics

### Features
- **Smart Language Detection**: Write in Georgian or English
- **Conversation Memory**: Bot remembers context until you clear it
- **Personal Assistant**: Help with work, learning, creativity
- **Interactive Menus**: Use inline buttons for easy navigation

### Example Conversations

**Georgian:**
```
User: გამარჯობა! როგორ ხარ?
Bot: 👋 გამარჯობა! კარგად ვარ, გმადლობთ! 😊 როგორ შემიძლია დაგეხმარო დღეს?
```

**English:**
```
User: Hello! How are you?
Bot: 👋 Hello! I'm doing great, thank you! 😊 How can I help you today?
```

## 🛠️ Development

### Project Structure
```
telegram-bot/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── .env              # Environment variables
├── README.md         # This file
└── ai_agent.db       # SQLite database (created automatically)
```

### Database Schema
- `chat_context` - Conversation history
- `user_profiles` - User information
- `user_preferences` - User settings

### Adding New Features

1. **New Commands**: Add handlers in `bot.py`
2. **Database Changes**: Modify schema in `init_db()`
3. **Language Support**: Update `SYSTEM_PROMPTS` dictionary

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_TOKEN` | Bot token from BotFather | ✅ |
| `LANGDOCK_API_KEY` | Langdock API key | ✅ |
| `ADMIN_USER_ID` | Admin Telegram user ID | ❌ |
| `MAX_CONTEXT_LENGTH` | Max conversation history | ❌ |
| `LOG_LEVEL` | Logging level | ❌ |

### Performance Tuning

- **Context Length**: Adjust `MAX_CONTEXT_LENGTH` (default: 20)
- **Response Length**: Modify `MAX_TOKENS` (default: 3000)
- **Temperature**: Change `TEMPERATURE` for creativity (default: 0.7)

## 📊 Monitoring

### Logs
```bash
# View Railway logs
railway logs

# Local logs
python bot.py
```

### Health Check
The bot includes a health check endpoint for monitoring.

## 🔒 Security

- Environment variables for sensitive data
- No hardcoded tokens
- SQLite database with proper indexing
- Error handling and logging

## 🆘 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check token validity
   - Verify Langdock API key
   - Check Railway logs

2. **Database errors**
   - Ensure write permissions
   - Check disk space

3. **API errors**
   - Verify Langdock account status
   - Check API rate limits

### Getting Help

1. Check Railway logs: `railway logs`
2. Test locally first
3. Verify all environment variables
4. Check Langdock dashboard for API status

## 📈 Scaling

### For High Traffic
- Upgrade Railway plan
- Consider PostgreSQL for database
- Implement Redis for caching
- Add rate limiting

### Multiple Languages
- Add new language patterns in `detect_language()`
- Update `SYSTEM_PROMPTS` dictionary
- Add language-specific keyboards

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Aiogram](https://aiogram.dev/) - Telegram Bot framework
- [Anthropic](https://anthropic.com/) - Claude AI model
- [Langdock](https://langdock.com/) - Free Claude API access
- [Railway](https://railway.app/) - Deployment platform

---

**Made with ❤️ for the Georgian and English speaking communities**

🤖 **Your AI Personal Assistant is ready to help!**
