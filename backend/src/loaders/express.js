import cors from 'cors';
import { json, urlencoded } from 'express';
import helmet from 'helmet';
import morgan from 'morgan';
import errorHandler from '../middleware/errorHandler.js';
import AuthRoutes from '../routes/AuthRoutes.js';
import profileRoutes from '../routes/ProfileRoutes.js';
import documentRoutes from '../routes/DocumentRoutes.js';

function loadExpress(app) {
  app.use(json());
  app.use(urlencoded({ extended: true }));
  app.use(helmet());
  app.use(cors());
  app.use(morgan('dev'));

  // API versioning
  app.use('/api/v1/auth', AuthRoutes);
  app.use(`/api/v1/user`, profileRoutes);
  app.use(`/api/v1/document`, documentRoutes);

  // Health check
  app.get('/health', (req, res) =>
    res.status(200).json({ success: true, message: 'Healthy' }),
  );

  // Error handler (last middleware)
  app.use(errorHandler);
}

export default loadExpress;
