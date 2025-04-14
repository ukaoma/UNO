#!/bin/bash

# Set text colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  Ukaoma Image Generation - Setup Script ${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed.${NC}"
    echo "Please install Python 3.9 or higher before continuing."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo -e "${RED}Error: pip is not installed.${NC}"
    echo "Please make sure pip is installed with your Python installation."
    exit 1
fi

# Install the UI dependencies
echo -e "${GREEN}Installing UI dependencies...${NC}"
python -m pip install -r requirements_ui.txt

# Success message
echo -e "\n${GREEN}Installation complete!${NC}"
echo -e "You can now run the UI with: ${BLUE}python app.py${NC}"
echo -e "The interface will open automatically in your web browser."
echo -e "\nEnjoy creating amazing images with your M3 Ultra!\n"
