#!/bin/bash
# Quick start script for TMG Market Research Platform

echo "🚀 Starting TMG Market Research Platform"
echo "========================================"
echo ""
echo "This will:"
echo "  • Start PostgreSQL database"
echo "  • Build and start backend (with migrations)"
echo "  • Build and start frontend"
echo "  • Create sample Monster Energy survey"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose first."
    exit 1
fi

# Start services
docker-compose up --build

echo ""
echo "👋 Services stopped. Run './start.sh' to start again."
