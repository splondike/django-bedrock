FROM node:18

CMD npm start

ENV NODE_ENV=development \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PATH=/app/node_modules/.bin:$PATH

WORKDIR /app
COPY package.json package-lock.json /app/

RUN npm ci --loglevel error
