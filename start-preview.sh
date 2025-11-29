#!/bin/bash
# Start preview server for AffineDrift website

echo "Starting AffineDrift website preview..."
echo ""
echo "The website will be available at:"
echo "  http://localhost:8080"
echo ""
echo "Key pages:"
echo "  - http://localhost:8080/index.html (Homepage)"
echo "  - http://localhost:8080/articles.html (Articles)"
echo "  - http://localhost:8080/contact.html (Contact with About)"
echo "  - http://localhost:8080/_site/articles/wrist-universal-joint.html (Quarto article)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start server in background and show output
python -m http.server 8080






