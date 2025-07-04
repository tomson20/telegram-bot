#!/bin/bash

# AI Personal Assistant Telegram Bot - Deployment Script
# This script helps you deploy your bot to Railway

set -e

echo "🤖 AI Personal Assistant Bot - Deployment Helper"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    exit 1
fi

# Check if tokens are configured
if grep -q "YOUR_TELEGRAM_BOT_TOKEN_HERE" .env; then
    print_error "Please configure your TELEGRAM_TOKEN in .env file"
    exit 1
fi

if grep -q "YOUR_LANGDOCK_API_KEY_HERE" .env; then
    print_error "Please configure your LANGDOCK_API_KEY in .env file"
    exit 1
fi

print_status "Environment configuration looks good!"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI not found. Installing..."
    
    # Install Railway CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install railway
        else
            print_error "Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://railway.app/install.sh | sh
    else
        print_error "Unsupported OS. Please install Railway CLI manually: https://docs.railway.app/develop/cli"
        exit 1
    fi
fi

print_status "Railway CLI is available"

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    print_info "Please log in to Railway..."
    railway login
fi

print_status "Logged in to Railway"

# Test bot configuration
print_info "Testing bot configuration..."
if python3 test_bot.py; then
    print_status "Bot configuration test passed!"
else
    print_error "Bot configuration test failed. Please fix the issues and try again."
    exit 1
fi

# Ask user if they want to deploy
echo ""
read -p "Do you want to deploy to Railway now? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Deploying to Railway..."
    
    # Initialize Railway project if not exists
    if [ ! -f "railway.json" ]; then
        print_info "Initializing Railway project..."
        railway init
    fi
    
    # Deploy
    print_info "Starting deployment..."
    railway up
    
    print_status "Deployment initiated!"
    print_info "You can monitor the deployment at: https://railway.app/dashboard"
    
    # Set environment variables
    print_info "Setting environment variables..."
    
    # Read .env file and set variables
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ $key =~ ^[[:space:]]*# ]] || [[ -z $key ]]; then
            continue
        fi
        
        # Remove quotes from value
        value=$(echo "$value" | sed 's/^"\(.*\)"$/\1/')
        
        # Set variable in Railway
        railway variables set "$key=$value"
        print_status "Set $key"
    done < .env
    
    print_status "Environment variables configured!"
    
    echo ""
    print_status "🎉 Deployment complete!"
    print_info "Your bot should be live in a few minutes."
    print_info "Check the Railway dashboard for logs and status."
    
else
    print_info "Deployment cancelled. You can deploy manually with: railway up"
fi

echo ""
print_info "Useful commands:"
echo "  railway logs     - View deployment logs"
echo "  railway status   - Check deployment status"
echo "  railway open     - Open Railway dashboard"
echo ""
print_status "Happy botting! 🤖"
