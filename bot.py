import asyncio
import logging
import sys
import re
from os import getenv
from datetime import datetime, timedelta
from typing import Optional, Dict, List

import aiosqlite
from dotenv import load_dotenv
from anthropic import Anthropic, APIError
from chatgpt_md_converter import telegram_format

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Load environment variables
load_dotenv(override=True)

# --- Configuration ---
TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
LANGDOCK_API_KEY = getenv("LANGDOCK_API_KEY")
ADMIN_USER_ID = getenv("ADMIN_USER_ID")

# Anthropic/Langdock API settings
ANTHROPIC_BASE_URL = "https://api.langdock.com/anthropic/eu/"
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# Check required tokens
if not TELEGRAM_TOKEN or not LANGDOCK_API_KEY:
    sys.exit("Error: TELEGRAM_TOKEN and LANGDOCK_API_KEY must be set in .env file")

# --- Initialize Anthropic client ---
try:
    anthropic_client = Anthropic(
        base_url=ANTHROPIC_BASE_URL,
        api_key=LANGDOCK_API_KEY
    )
except Exception as e:
    sys.exit(f"Error initializing Anthropic client: {e}")

dp = Dispatcher()

# --- Database ---
DB_PATH = "ai_agent.db"

# Language detection patterns
GEORGIAN_PATTERN = re.compile(r'[\u10A0-\u10FF]')
ENGLISH_PATTERN = re.compile(r'[a-zA-Z]')

# System prompts for different languages
SYSTEM_PROMPTS = {
    'georgian': """შენ ხარ ძალიან ჭკვიანი და მეგობრული AI პერსონალური ასისტენტი. შენი მიზანია:

🎯 **ძირითადი მიზნები:**
- იყო მომხმარებლის პერსონალური ასისტენტი და მეგობარი
- დაეხმარო ნებისმიერ საკითხში - სამუშაოდან პირადულ ცხოვრებამდე
- იყო შემოქმედებითი, ემპათიური და მხარდამჭერი
- ინახავდე კონტექსტს და ისწავლო მომხმარებლის უპირატესობები

💬 **კომუნიკაციის სტილი:**
- იყო ბუნებრივი და მეგობრული, არა ფორმალური
- გამოიყენე ემოჯი გრძნობების გადმოსაცემად
- იყო კონკრეტული და სასარგებლო
- ნუ იქნები ზედმეტად ვრცელი, თუ არ არის საჭირო

🧠 **შენი შესაძლებლობები:**
- ანალიზი და რჩევები
- შემოქმედებითი დახმარება
- სწავლებისა და ახსნის დახმარება
- ემოციური მხარდაჭერა
- დაგეგმვა და ორგანიზება
- ტექნიკური დახმარება

დაიმახსოვრე: შენ ხარ მომხმარებლის პერსონალური AI მეგობარი, რომელიც ყოველთვის მზადაა დასახმარებლად! 🤖✨""",

    'english': """You are a highly intelligent and friendly AI personal assistant. Your mission is to:

🎯 **Core Objectives:**
- Be the user's personal assistant and friend
- Help with anything - from work to personal life
- Be creative, empathetic, and supportive
- Maintain context and learn user preferences

💬 **Communication Style:**
- Be natural and friendly, not formal
- Use emojis to convey emotions
- Be specific and helpful
- Don't be overly verbose unless needed

🧠 **Your Capabilities:**
- Analysis and advice
- Creative assistance
- Learning and explanation help
- Emotional support
- Planning and organization
- Technical assistance

Remember: You are the user's personal AI friend, always ready to help! 🤖✨""",

    'mixed': """You are a multilingual AI personal assistant. Respond in the same language the user writes to you.

თუ მომხმარებელი ქართულად წერს - უპასუხე ქართულად.
If the user writes in English - respond in English.

🎯 Be helpful, friendly, and maintain conversation context.
🤖 You're a personal AI assistant and friend!"""
}

async def init_db():
    """Initialize database with enhanced schema"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Chat context table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User profiles table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                preferred_language TEXT DEFAULT 'mixed',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
        """)
        
        # User preferences table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                context_length INTEGER DEFAULT 20,
                response_style TEXT DEFAULT 'balanced',
                timezone TEXT DEFAULT 'UTC',
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        """)
        
        # Create indexes
        await db.execute("CREATE INDEX IF NOT EXISTS idx_user_id_timestamp ON chat_context(user_id, timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_user_last_active ON user_profiles(last_active)")
        
        await db.commit()

async def detect_language(text: str) -> str:
    """Detect language of the text"""
    georgian_chars = len(GEORGIAN_PATTERN.findall(text))
    english_chars = len(ENGLISH_PATTERN.findall(text))
    
    if georgian_chars > english_chars:
        return 'georgian'
    elif english_chars > georgian_chars:
        return 'english'
    else:
        return 'mixed'

async def update_user_profile(message: Message):
    """Update or create user profile"""
    user = message.from_user
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO user_profiles 
            (user_id, username, first_name, last_name, last_active, message_count)
            VALUES (?, ?, ?, ?, ?, 
                COALESCE((SELECT message_count FROM user_profiles WHERE user_id = ?), 0) + 1)
        """, (user.id, user.username, user.first_name, user.last_name, datetime.now(), user.id))
        
        # Initialize preferences if not exists
        await db.execute("""
            INSERT OR IGNORE INTO user_preferences (user_id) VALUES (?)
        """, (user.id,))
        
        await db.commit()

async def add_message_to_context(user_id: int, role: str, content: str):
    """Add message to user context with intelligent cleanup"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO chat_context (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        
        # Get user's preferred context length
        cursor = await db.execute(
            "SELECT context_length FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()
        context_length = result[0] if result else 20
        
        # Keep only recent messages
        await db.execute("""
            DELETE FROM chat_context 
            WHERE user_id = ? AND id NOT IN (
                SELECT id FROM chat_context 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            )
        """, (user_id, user_id, context_length))
        
        await db.commit()

async def get_user_context(user_id: int) -> List[Dict]:
    """Get user conversation context"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT role, content FROM chat_context WHERE user_id = ? ORDER BY timestamp ASC",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in rows]

async def clear_user_context(user_id: int):
    """Clear user conversation context"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM chat_context WHERE user_id = ?", (user_id,))
        await db.commit()

async def get_user_stats(user_id: int) -> Dict:
    """Get user statistics"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT message_count, created_at, preferred_language 
            FROM user_profiles WHERE user_id = ?
        """, (user_id,))
        result = await cursor.fetchone()
        
        if result:
            return {
                'message_count': result[0],
                'member_since': result[1],
                'preferred_language': result[2]
            }
        return {}

def create_main_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create main menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    if language == 'georgian':
        builder.row(
            InlineKeyboardButton(text="🗑️ ახალი საუბარი", callback_data="newchat"),
            InlineKeyboardButton(text="📊 სტატისტიკა", callback_data="stats")
        )
        builder.row(
            InlineKeyboardButton(text="⚙️ პარამეტრები", callback_data="settings"),
            InlineKeyboardButton(text="ℹ️ დახმარება", callback_data="help")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="🗑️ New Chat", callback_data="newchat"),
            InlineKeyboardButton(text="📊 Statistics", callback_data="stats")
        )
        builder.row(
            InlineKeyboardButton(text="⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton(text="ℹ️ Help", callback_data="help")
        )
    
    return builder.as_markup()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Handle /start command"""
    await update_user_profile(message)
    user_lang = await detect_language(message.text) if len(message.text) > 6 else 'mixed'
    
    if user_lang == 'georgian':
        welcome_text = f"""
👋 გამარჯობა, <b>{message.from_user.full_name}</b>!

🤖 მე ვარ შენი პერსონალური AI ასისტენტი, რომელიც იყენებს <code>{ANTHROPIC_MODEL}</code> მოდელს.

✨ <b>რას შემიძლია:</b>
• ვუპასუხო ნებისმიერ კითხვას ქართულად და ინგლისურად
• ვინახავ ჩვენი საუბრის კონტექსტს
• დაგეხმარო სამუშაოში, სწავლაში, შემოქმედებაში
• ვიყო შენი AI მეგობარი და ასისტენტი

💬 უბრალოდ დამწერე რაიმე და დავიწყოთ საუბარი!
        """
    else:
        welcome_text = f"""
👋 Hello, <b>{message.from_user.full_name}</b>!

🤖 I'm your personal AI assistant powered by <code>{ANTHROPIC_MODEL}</code>.

✨ <b>What I can do:</b>
• Answer any questions in Georgian and English
• Remember our conversation context
• Help with work, learning, creativity
• Be your AI friend and assistant

💬 Just write me anything and let's start chatting!
        """
    
    keyboard = create_main_keyboard(user_lang)
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message(Command("newchat"))
async def newchat_handler(message: Message) -> None:
    """Handle /newchat command"""
    await clear_user_context(message.from_user.id)
    user_lang = await detect_language(message.text) if len(message.text) > 8 else 'mixed'
    
    if user_lang == 'georgian':
        text = "🗑️ საუბრის კონტექსტი გაიწმინდა!\nახლა შეგიძლია ახალი თემა დაიწყო."
    else:
        text = "🗑️ Conversation context cleared!\nYou can now start a new topic."
    
    await message.answer(text)

@dp.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    """Handle /stats command"""
    stats = await get_user_stats(message.from_user.id)
    user_lang = await detect_language(message.text) if len(message.text) > 6 else 'mixed'
    
    if stats:
        if user_lang == 'georgian':
            text = f"""
📊 <b>შენი სტატისტიკა:</b>

💬 შეტყობინებები: {stats['message_count']}
📅 წევრობა: {stats['member_since'][:10]}
🌐 ენა: {stats['preferred_language']}
            """
        else:
            text = f"""
📊 <b>Your Statistics:</b>

💬 Messages: {stats['message_count']}
📅 Member since: {stats['member_since'][:10]}
🌐 Language: {stats['preferred_language']}
            """
    else:
        text = "📊 No statistics available yet."
    
    await message.answer(text)

@dp.message(F.text)
async def message_handler(message: Message):
    """Handle text messages with AI response"""
    # Update user profile
    await update_user_profile(message)
    
    # Detect language
    user_lang = await detect_language(message.text)
    
    # Show thinking message
    if user_lang == 'georgian':
        thinking_msg = await message.answer("🤔 ვფიქრობ...")
    else:
        thinking_msg = await message.answer("🤔 Thinking...")
    
    user_id = message.from_user.id
    
    try:
        # Add user message to context
        await add_message_to_context(user_id, "user", message.text)
        
        # Get conversation context
        context_messages = await get_user_context(user_id)
        
        # Choose system prompt based on detected language
        system_prompt = SYSTEM_PROMPTS.get(user_lang, SYSTEM_PROMPTS['mixed'])
        
        # Telegram formatting instructions
        telegram_format_prompt = """
When formatting responses for Telegram, use these conventions:

1. For spoiler content: ||spoiler text||
2. For expandable sections: **> Section Title
   > Content line 1
   > Content line 2

3. Standard markdown:
   - **bold text**
   - *italic*
   - __underlined__
   - ~~strikethrough~~
   - `inline code`
   - ```code blocks```
   - [link text](URL)
"""
        
        # Prepare API messages
        api_messages = [
            {"role": "user", "content": f"{system_prompt}\n\n{telegram_format_prompt}"},
            {"role": "assistant", "content": "Understood! I'll use the specified formats and follow the instructions."}
        ]
        
        # Add conversation context
        api_messages.extend(context_messages)
        
        # Call Anthropic API
        response = anthropic_client.messages.create(
            model=ANTHROPIC_MODEL,
            messages=api_messages,
            max_tokens=3000,
            temperature=0.7
        )
        
        ai_answer = response.content[0].text
        
        # Add AI response to context
        await add_message_to_context(user_id, "assistant", ai_answer)
        
        # Format for Telegram
        formatted_answer = telegram_format(ai_answer)
        
        # Edit the thinking message with the response
        await thinking_msg.edit_text(formatted_answer)
        
    except APIError as e:
        logging.error(f"Anthropic API error: {e}")
        error_msg = "😕 API error occurred. Please try again later." if user_lang == 'english' else "😕 API შეცდომა მოხდა. სცადეთ მოგვიანებით."
        await thinking_msg.edit_text(error_msg)
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        error_msg = "😕 Something went wrong. Please contact admin." if user_lang == 'english' else "😕 რაღაც არასწორად მოხდა. დაუკავშირდით ადმინს."
        await thinking_msg.edit_text(error_msg)

# Callback query handlers
@dp.callback_query(F.data == "newchat")
async def callback_newchat(callback):
    await clear_user_context(callback.from_user.id)
    await callback.answer("🗑️ Context cleared!")
    await callback.message.edit_text("🗑️ Conversation context cleared!\nYou can start a new topic now.")

@dp.callback_query(F.data == "stats")
async def callback_stats(callback):
    stats = await get_user_stats(callback.from_user.id)
    if stats:
        text = f"""
📊 <b>Your Statistics:</b>

💬 Messages: {stats['message_count']}
📅 Member since: {stats['member_since'][:10]}
🌐 Language: {stats['preferred_language']}
        """
    else:
        text = "📊 No statistics available yet."
    
    await callback.answer()
    await callback.message.edit_text(text)

@dp.callback_query(F.data == "help")
async def callback_help(callback):
    help_text = """
🤖 <b>AI Personal Assistant Help</b>

<b>Available Commands:</b>
/start - Start the bot
/newchat - Clear conversation context
/stats - View your statistics

<b>Features:</b>
• Multilingual support (Georgian/English)
• Conversation memory
• Personal assistant capabilities
• Context-aware responses

<b>Tips:</b>
• Write in Georgian or English - I'll respond in the same language
• I remember our conversation until you start a new chat
• Ask me anything - I'm here to help!

💡 Just start typing to begin our conversation!
    """
    
    await callback.answer()
    await callback.message.edit_text(help_text)

async def main() -> None:
    """Main function"""
    # Initialize database
    await init_db()
    
    # Initialize bot
    bot = Bot(
        token=TELEGRAM_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Start polling
    logging.info("🚀 AI Personal Assistant Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    asyncio.run(main())
