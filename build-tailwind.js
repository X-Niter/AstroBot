// build-tailwind.js
const { execSync } = require('child_process');
const path = require('path');

try {
  console.log('Building Tailwind CSS...');
  // Use local node_modules instead of npx
  const tailwindBinPath = path.join(__dirname, 'node_modules', '.bin', 'tailwindcss');
  
  execSync(`${tailwindBinPath} -i ./static/css/tailwind.css -o ./static/css/output.css --minify`);
  console.log('Tailwind CSS built successfully!');
} catch (error) {
  console.error('Error building Tailwind CSS:', error);
  process.exit(1);
}