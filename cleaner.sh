#!/bin/bash

echo "=== Docker Compose Reset Script ==="
echo "This will:"
echo "1. Stop and remove all containers"
echo "2. Remove all unused images"
echo "3. Rebuild services with no cache"
echo "4. Start services in detached mode"

set -e  # Exit immediately on error

# Step 1: Clean up containers
echo -e "\n[1/4] Stopping and removing containers..."
docker-compose down -v

# Step 2: Prune system
echo -e "\n[2/4] Pruning Docker system..."
docker system prune -a -f

# Step 3: Rebuild
echo -e "\n[3/4] Rebuilding services with no cache..."
docker-compose build --no-cache

# Step 4: Start services
echo -e "\n[4/4] Starting services..."
docker-compose up -d

echo -e "\nSUCCESS: All operations completed"
echo "Check running containers with: docker-compose ps"
