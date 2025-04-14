#!/bin/bash

# Set text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "\n${GREEN}Stopping Ukaoma Image Generator processes...${NC}"

# Find Python processes running app.py
PIDS=$(ps aux | grep "python app.py" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
  echo -e "${RED}No running app.py processes found.${NC}"
else
  # Kill each process
  for PID in $PIDS; do
    echo -e "Killing process with PID: ${RED}$PID${NC}"
    kill -9 $PID
  done
  echo -e "${GREEN}Application processes terminated.${NC}"
fi

# Additionally check for any processes on port 7860 (default Gradio port)
PORT_PID=$(lsof -i:7860 -t 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
  echo -e "Found process on Gradio port (7860): ${RED}$PORT_PID${NC}"
  kill -9 $PORT_PID
  echo -e "${GREEN}Port 7860 freed.${NC}"
fi

echo -e "\n${GREEN}Done.${NC}"
