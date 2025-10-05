import 'dotenv/config'; // ✅ loads .env automatically
import express from 'express';
import loadExpress from './loaders/express.js';

function createApp() {
  const app = express();
  loadExpress(app);
  return app;
}

export default createApp;
