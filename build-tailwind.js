// build-tailwind.js
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Ensure directories exist
const dirs = ['./static/css/dist'];
dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Use local node_modules instead of npx
const tailwindBinPath = path.join(__dirname, 'node_modules', '.bin', 'tailwindcss');

// Build tailwind CSS
try {
  console.log('Building Tailwind CSS...');
  execSync(`${tailwindBinPath} -i ./static/css/tailwind.css -o ./static/css/dist/tailwind.css`, { stdio: 'inherit' });
  console.log('Tailwind CSS built successfully!');
} catch (error) {
  console.error('Error building Tailwind CSS:', error.message);
  process.exit(1);
}

// Also create a minified version
try {
  console.log('Creating minified version...');
  execSync(`${tailwindBinPath} -i ./static/css/tailwind.css -o ./static/css/dist/tailwind.min.css --minify`, { stdio: 'inherit' });
  console.log('Minified version created successfully!');
} catch (error) {
  console.error('Error creating minified version:', error.message);
  process.exit(1);
}

console.log('Build completed!');