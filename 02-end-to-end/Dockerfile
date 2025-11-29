FROM node:18-alpine

WORKDIR /app

# Copy root package.json (if any) or just setup structure
# We will copy everything and build

COPY . .

# Install dependencies and build client
WORKDIR /app/client
RUN npm install
RUN npm run build

# Install server dependencies
WORKDIR /app/server
RUN npm install

# Expose port
EXPOSE 3001

# Start server
CMD ["npm", "start"]
