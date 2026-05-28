const fs = require('fs');

let content = fs.readFileSync('script.js', 'utf8');
if (content.includes('const focusableContent = lightbox.querySelectorAll(focusableSelector);')) {
    console.log('Found querySelectorAll call in script.js for focusableContent');
} else {
    console.log('Not found in script.js');
}

let access_content = fs.readFileSync('js/accessibility.js', 'utf8');
if (access_content.includes('const focusableContent = modal.querySelectorAll(')) {
    console.log('Found querySelectorAll call in js/accessibility.js');
} else {
    console.log('Not found in accessibility.js');
}
