#!/bin/bash
# Simple script to preview just the articles

echo "Rendering articles..."
quarto render articles/*.qmd --to html

echo ""
echo "Starting preview server for articles..."
echo "Open your browser to: http://localhost:4200"
echo ""
echo "Press Ctrl+C to stop the preview server"
echo ""

# Start a simple HTTP server to preview the rendered articles
cd _site/articles
python -m http.server 4200 2>/dev/null || python3 -m http.server 4200 2>/dev/null || echo "Python HTTP server not available. Please open _site/articles/ in your browser manually."

