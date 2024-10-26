# Build Next.js app
FROM node:20-alpine as builder

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install --only=production

COPY . .

RUN npm run build

# Production image
FROM node:20-alpine

WORKDIR /usr/src/app

COPY package*.json ./

COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY --from=builder /usr/src/app/.next ./.next
COPY --from=builder /usr/src/app/public ./public

EXPOSE 3000
CMD ["npm", "start"]