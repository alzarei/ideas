# Test Dockerfile for clean machine setup validation
# This simulates a completely fresh environment with only basic OS tools

FROM ubuntu:22.04

# Set environment to non-interactive to avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install minimal system dependencies (simulating a clean machine)
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create a test user (simulating a regular user, not root)
RUN useradd -m -s /bin/bash testuser
USER testuser
WORKDIR /home/testuser

# Copy the project files
COPY --chown=testuser:testuser . ./on-device-slm/
WORKDIR /home/testuser/on-device-slm

# Test script that will run our quick setup
RUN echo '#!/bin/bash\n\
set -e\n\
echo "=== TESTING CLEAN MACHINE SETUP ==="\n\
echo "Starting with completely fresh environment..."\n\
echo "Python check:"\n\
python3 --version || echo "Python not installed"\n\
echo "Node.js check:"\n\
node --version || echo "Node.js not installed"\n\
echo "npm check:"\n\
npm --version || echo "npm not installed"\n\
echo "git check:"\n\
git --version || echo "git not installed"\n\
echo "Ollama check:"\n\
ollama --version || echo "Ollama not installed"\n\
echo ""\n\
echo "=== RUNNING ULTRA QUICK SETUP ==="\n\
python3 ultra_quick_setup.py\n\
echo ""\n\
echo "=== SETUP COMPLETE - TESTING APPLICATION ==="\n\
# Test if we can start the application in background\n\
timeout 30s python3 launcher.py &\n\
sleep 10\n\
# Test if the application is responding\n\
curl -f http://localhost:8000/api/health || echo "Health check failed"\n\
echo "=== TEST COMPLETE ==="\n\
' > test_setup.sh && chmod +x test_setup.sh

# The test will be run when container starts
CMD ["./test_setup.sh"]
