#!/bin/bash

echo "Building Pharmaceutical News Dashboard..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Copy data files
echo "Copying data files..."
mkdir -p static/data
cp ../data/*.json static/data/ 2>/dev/null || echo "No data files found"

# Create manifest
echo "Creating data manifest..."
cd static/data
echo '{"files":[' > manifest.json
first=true
for file in *.json; do
    if [ "$file" != "manifest.json" ] && [ -f "$file" ]; then
        if [ "$first" = true ]; then
            first=false
        else
            echo -n ',' >> manifest.json
        fi
        echo -n "\"$file\"" >> manifest.json
    fi
done
echo ']}' >> manifest.json
cd ../..

# Build the app
echo "Building SvelteKit app..."
npm run build

echo "Build complete! To preview: npm run preview"