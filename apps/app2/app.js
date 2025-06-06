const express = require('express');
const winston = require('winston');
const app = express();
const leak = [];

// Configure logging
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [
        new winston.transports.Console()
    ]
});

// In apps/app2/app.js
const promBundle = require("express-prom-bundle");
const metricsMiddleware = promBundle({
  includeMethod: true,
  includePath: true
});

app.use(metricsMiddleware);

// Add explicit metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', promBundle.promClient.register.contentType);
  res.end(promBundle.promClient.register.metrics());
});

app.get('/', (req, res) => {
    logger.info('App2 health check', {app: 'app2', type: 'healthcheck'});
    res.send('App2 Running OK');
});

app.get('/leak', (req, res) => {
    logger.warn('Memory leak triggered', {app: 'app2', type: 'leak'});
    for(let i = 0; i < 100000; i++) {
        leak.push(new Array(1000));
    }
    res.send('Memory leak triggered');
});

app.get('/health', (req, res) => {
    res.status(200).send('OK');
});

app.listen(3000, () => {
    console.log('App2 listening on port 3000');
});