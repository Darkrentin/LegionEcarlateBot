#!/bin/bash

# Virtual environment name
VENV_NAME="venv"

echo "--- Setting up environment for the bot ---"

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "ERROR: python3 is not installed. Please install it to continue."
    exit 1
fi

# 1. Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment '$VENV_NAME'..."
    python3 -m venv $VENV_NAME
else
    echo "Virtual environment '$VENV_NAME' already exists."
fi

# 2. Activate the virtual environment
# Note: Activation is specific to this script.
# If you exit the script, you will need to reactivate it manually with `source venv/bin/activate`
source "$VENV_NAME/bin/activate"
echo "Virtual environment activated."

# 3. Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo "Dependencies installed successfully."

# 4. Configure the .env file with the bot token
if [ ! -f ".env" ] || ! grep -q "TOKEN=" ".env"; then
    echo "The .env file or the TOKEN variable is missing."
    read -p "Please enter your Discord bot TOKEN: " BOT_TOKEN
    echo "TOKEN=$BOT_TOKEN" > .env
    echo "The .env file has been created/updated."
else
    echo "The .env file with the TOKEN already exists."
fi

# 5. Launch the bot
echo "--- Starting the bot ---"
python3 bot.py

# Deactivate the virtual environment when the script ends (Ctrl+C to stop the bot)
deactivate
echo "--- Script finished ---"