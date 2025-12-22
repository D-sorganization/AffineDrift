# Quarto Preview - Access Instructions

## Preview Server

Quarto preview has been started in the background. The preview server should be accessible at:

**http://localhost:4200**

(If port 4200 is busy, Quarto will automatically use the next available port: 4201, 4202, etc.)

## How to Access

1. **Open your web browser**
2. **Navigate to**: `http://localhost:4200`
3. The site will auto-reload when you make changes to `.qmd` files

## What You'll See

- **Homepage**: Main index page
- **Articles**:
  - `/articles/wrist-universal-joint.html` - Wrist Universal Joint article
  - `/articles/inverse-dynamics.html` - Inverse Dynamics article
- **Navigation**: All navbar links should work
- **Math Equations**: Rendered with MathJax
- **Code Blocks**: With syntax highlighting

## Stopping the Preview

To stop the preview server:

- Press `Ctrl+C` in the terminal where it's running
- Or close the terminal window
- Or find the process and kill it

## Troubleshooting

If the preview doesn't load:

1. Check that Quarto is running: Look for the process in Task Manager
2. Try a different port: `quarto preview --port 4201`
3. Check for errors in the terminal output
4. Verify articles render: `quarto render articles/wrist-universal-joint.qmd`

## Testing Checklist

While preview is running, test:

- [ ] Homepage loads correctly
- [ ] Navigation links work
- [ ] Articles display properly
- [ ] Math equations render (MathJax)
- [ ] Code blocks have syntax highlighting
- [ ] Links to calculator tools work
- [ ] Mobile responsive (resize browser window)
