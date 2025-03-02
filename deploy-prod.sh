#!/bin/bash

# Deploy production environment using docker-compose.prod.yml

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
  echo "Error: .env.prod file not found!"
  echo "Please create .env.prod file with your RDS credentials."
  echo "You can use .env.prod.example as a template."
  exit 1
fi

# Load environment variables from .env.prod
export $(grep -v '^#' .env.prod | xargs)

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d

echo "Production environment deployed successfully!"
echo "Your application is now running with RDS database."
