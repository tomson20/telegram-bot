#!/usr/bin/env python3
"""
Setup script for AI Personal Assistant Telegram Bot
This script helps you configure your bot for the first time
"""

import os
import sys
import re
from pathlib import Path

def print_header():
    print("🤖 AI Personal Assistant Bot - Setup Wizard")
    print("=" * 50)
    print()

def print_step(step, title):
    print(f"📋 Step {step}: {title}")
    print("-" * 30)

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def validate_telegram_token(token):
    """Validate Telegram bot token format"""
    pattern = r'^\d+:[A-Za-z0-9_-]{35}$'
    return re.match(pattern, token) is not None

def validate_langdock_key(key):
    """Basic validation for Langdock API key"""
    return len(key) > 10 and key.startswith(('sk-', 'ld-'))

def setup_environment():
    """Setup environment variables"""
    print_step(1, "Environment Configuration")
    
    env_file = Path(".env")
    
    # Read current .env
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
    else:
        print_error(".env file not found!")
        return False
    
    # Get Telegram token
    print("\n🔑 Telegram Bot Token")
    print("Get your token from @BotFather on Telegram:")
    print("1. Message @BotFather")
    print("2. Send /newbot")
    print("3. Follow instructions")
    print("4. Copy the token")
    print()
    
    while True:
        telegram_token = input("Enter your Telegram bot token: ").strip()
        if validate_telegram_token(telegram_token):
            print_success("Valid Telegram token format")
            break
        else:
            print_error("Invalid token format. Should be like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
    
    # Get Langdock API key
    print("\n🔑 Langdock API Key")
    print("Get your free Claude API key from Langdock:")
    print("1. Visit https://langdock.com")
    print("2. Sign up for free account")
    print("3. Go to API section")
    print("4. Generate API key")
    print()
    
    while True:
        langdock_key = input("Enter your Langdock API key: ").strip()
        if validate_langdock_key(langdock_key):
            print_success("Valid Langdock API key format")
            break
        else:
            print_error("Invalid API key format. Should start with 'sk-' or 'ld-'")
    
    # Optional: Admin user ID
    print("\n👤 Admin User ID (Optional)")
    print("Your Telegram user ID for admin features:")
    print("You can get it from @userinfobot on Telegram")
    admin_id = input("Enter your Telegram user ID (or press Enter to skip): ").strip()
    
    # Update .env file
    env_content = env_content.replace('YOUR_TELEGRAM_BOT_TOKEN_HERE', telegram_token)
    env_content = env_content.replace('YOUR_LANGDOCK_API_KEY_HERE', langdock_key)
    
    if admin_id:
        env_content = env_content.replace('YOUR_TELEGRAM_USER_ID', admin_id)
    
    # Write updated .env
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print_success("Environment configuration saved!")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step(2, "Installing Dependencies")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Dependencies installed successfully!")
            return True
        else:
            print_error(f"Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Error installing dependencies: {e}")
        return False

def test_configuration():
    """Test the bot configuration"""
    print_step(3, "Testing Configuration")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'test_bot.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Configuration test passed!")
            print("📝 Test output:")
            print(result.stdout)
            return True
        else:
            print_error("Configuration test failed!")
            print("📝 Error output:")
            print(result.stderr)
            return False
    except Exception as e:
        print_error(f"Error running tests: {e}")
        return False

def show_next_steps():
    """Show next steps to user"""
    print_step(4, "Next Steps")
    
    print("🎉 Setup complete! Here's what you can do next:")
    print()
    print("🔧 Local Testing:")
    print("   python bot.py")
    print()
    print("🚀 Deploy to Railway:")
    print("   ./deploy.sh")
    print("   (or follow manual instructions in README.md)")
    print()
    print("📚 Documentation:")
    print("   Check README.md for detailed instructions")
    print()
    print("🆘 Need Help?")
    print("   - Check the troubleshooting section in README.md")
    print("   - Test your configuration: python test_bot.py")
    print("   - Verify your tokens are correct")
    print()
    print_success("Your AI Personal Assistant Bot is ready! 🤖")

def main():
    """Main setup function"""
    print_header()
    
    # Check if Python version is compatible
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ is required")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path("bot.py").exists():
        print_error("bot.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    print_info("Welcome to the AI Personal Assistant Bot setup!")
    print_info("This wizard will help you configure your bot.")
    print()
    
    # Step 1: Environment setup
    if not setup_environment():
        print_error("Environment setup failed!")
        sys.exit(1)
    
    print()
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print_error("Dependency installation failed!")
        sys.exit(1)
    
    print()
    
    # Step 3: Test configuration
    if not test_configuration():
        print_warning("Configuration test failed, but you can still proceed.")
        print_warning("Make sure to fix any issues before deploying.")
    
    print()
    
    # Step 4: Show next steps
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
