#!/bin/bash

# Enable build flags
export ENABLE_ORYX_BUILD=true
export SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

echo "Build completed successfully"
