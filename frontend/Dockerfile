FROM node:20-alpine

WORKDIR /app

ENV WATCHPACK_POLLING=true

# Copy package files to leverage Docker cache
COPY package.json package-lock.json ./

# Install dependencies cleanly
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Start the Next.js development server
CMD ["npm", "run", "dev"]