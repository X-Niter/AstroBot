// build-tailwind.js
const { execSync } = require('child_process');

try {
  console.log('Building Tailwind CSS...');
  execSync('npx tailwindcss -i ./static/css/tailwind.css -o ./static/css/output.css --minify');
  console.log('Tailwind CSS built successfully!');
} catch (error) {
  console.error('Error building Tailwind CSS:', error);
  process.exit(1);
}