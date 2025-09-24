#!/bin/bash

# Digital Twin MedTech MVP - Simple Startup Script
echo "🏥 Starting Digital Twin MedTech MVP System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Start the API server in background
echo "🚀 Starting Digital Twin API server..."
python3 simple_app.py &
API_PID=$!

# Wait for API to start
echo "⏳ Waiting for API server to start..."
sleep 8

# Test the API
echo "🧪 Testing API connection..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API server is running successfully!"
    echo "📱 API is available at: http://localhost:8000"
    echo "🔍 Health check: http://localhost:8000/health"
    echo "👥 Patients: http://localhost:8000/patients"
    echo "📊 Dashboard data: http://localhost:8000/dashboard-data/overview"
else
    echo "❌ API server failed to start properly"
    kill $API_PID 2>/dev/null
    exit 1
fi

# Ask user if they want to run data simulation
echo ""
read -p "🔄 Would you like to run the data simulation demo? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 Running data simulation demo..."
    python3 simple_simulator.py demo
    echo ""
    echo "✨ Demo completed! The system now has sample data."
else
    echo "ℹ️ You can manually run demos with:"
    echo "   python3 simple_simulator.py demo          # Run demo scenario"
    echo "   python3 simple_simulator.py continuous    # Continuous simulation"
fi

echo ""
echo "📈 Next Steps:"
echo "1. 📊 Set up Power BI dashboard (see POWERBI_SETUP.md)"
echo "2. 🔄 Run continuous simulation: python3 simple_simulator.py continuous"
echo "3. 📱 Access API documentation at: http://localhost:8000"
echo ""
echo "🛑 To stop the API server, run: kill $API_PID"
echo "   Or press Ctrl+C in the terminal where the API is running"

# Keep script running until user stops it
echo "Press Ctrl+C to exit this script (API will continue running)"
trap 'echo "Script stopped. API server (PID: $API_PID) is still running."' INT
while true; do
    sleep 1
done