FROM node:20-alpine

# Install OS dependencies required by canvas (which might be used by qrcode/baileys)
RUN apk add --no-cache git python3 make build-base g++ cairo-dev jpeg-dev pango-dev giflib-dev

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 3001

CMD ["npm", "start"]
