#!/bin/bash

# Description: Updates the Git repository, builds the frontend with Yarn, and restarts Docker containers.
# Usage: ./script.sh

set -e  # Exit immediately on any error

# Change to the project directory
PROJECT_DIR="/opt/temp-ai-review"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory '$PROJECT_DIR' not found. Exiting."
    exit 1
fi

cd "$PROJECT_DIR" || { echo "❌ Failed to navigate to $PROJECT_DIR. Exiting."; exit 1; }

echo "🔄 Fetching latest changes from Git..."
if git fetch && git pull; then
    echo "✅ Git repository updated successfully."
else
    echo "❌ Failed to update the Git repository. Exiting."
    exit 1
fi

# Build frontend using Yarn
FRONTEND_DIR="./frontend"

if [ -d "$FRONTEND_DIR" ]; then
    echo "🚀 Building frontend..."
    pushd "$FRONTEND_DIR" > /dev/null || { echo "❌ Failed to enter $FRONTEND_DIR. Exiting."; exit 1; }

    if ! command -v yarn &> /dev/null; then
        echo "❌ Yarn is not installed. Please install Yarn before proceeding. Exiting."
        popd > /dev/null
        exit 1
    fi

    echo "📦 Installing dependencies..."
    yarn install && echo "✅ Dependencies installed successfully." || { echo "❌ Yarn install failed. Exiting."; popd > /dev/null; exit 1; }

    echo "🏗️ Building the project..."
    yarn build && echo "✅ Frontend built successfully." || { echo "❌ Frontend build failed. Exiting."; popd > /dev/null; exit 1; }

    popd > /dev/null
else
    echo "❌ Frontend directory '$FRONTEND_DIR' not found. Exiting."
    exit 1
fi

# Restart Docker containers
echo "🔍 Checking for docker-compose.yml..."
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in '$PROJECT_DIR'. Exiting."
    exit 1
fi

# Determine the correct Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose not found. Please install Docker and Docker Compose. Exiting."
    exit 1
fi

echo "🔄 Restarting Docker containers..."
$DOCKER_COMPOSE_CMD down && echo "✅ Docker containers stopped successfully." || { echo "❌ Failed to stop Docker containers. Exiting."; exit 1; }
$DOCKER_COMPOSE_CMD up -d && echo "✅ Docker containers started successfully." || { echo "❌ Failed to start Docker containers. Exiting."; exit 1; }

echo "🎉 ✅ Script executed successfully."
