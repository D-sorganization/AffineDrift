# Interactive Tools Directory

This directory contains interactive web-based tools and simulators that complement the articles on AffineDrift.

## Structure

Each tool has its own subdirectory containing:
- **JavaScript/HTML5 version** - Standalone HTML file that runs entirely in the browser
- **Streamlit version** - Python-based web app for deployment on Streamlit Cloud
- **Documentation** - Embedding guides and usage instructions
- **Requirements** - Dependencies for Streamlit deployment

## Current Tools

### `wrist-universal-joint/`
**Grip Angle Torque Transmission Simulator**

Interactive tool for analyzing how grip angle affects torque transmission and angular acceleration in golf swing biomechanics.

**Files:**
- `grip_angle_simulator.html` - JavaScript/HTML5 standalone version
- `Grip_Angle_Torque_Transmission_Streamlit.py` - Streamlit version
- `requirements.txt` - Python dependencies
- `EMBEDDING_GUIDE.md` - Complete embedding instructions

**Article:** [Wrists Behave as Universal Joints](../wrist-universal-joint.html)

## Adding New Tools

When transferring tools from external repositories:

1. **Create a new subdirectory** under `tools/` with a descriptive name
2. **Include both versions:**
   - JavaScript/HTML5 version (for direct GitHub Pages hosting)
   - Streamlit version (for cloud deployment)
3. **Add documentation:**
   - README.md in the tool directory
   - Embedding instructions
   - Usage guide
4. **Update this README** with the new tool
5. **Create/update article page** linking to the tool
6. **Add to articles.html** listing

## Deployment

- **JavaScript versions:** Work directly on GitHub Pages (no deployment needed)
- **Streamlit versions:** Deploy to [Streamlit Cloud](https://streamlit.io/cloud) and embed via iframe

## CI/CD

Tools are validated as part of the main repository CI/CD pipeline:
- HTML files are validated
- Python files are checked for syntax
- All tools must pass validation before deployment

See `.github/workflows/deploy.yml` for details.









