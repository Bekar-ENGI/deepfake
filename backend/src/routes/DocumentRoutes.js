import { Router } from 'express';
import FileUpload from '../utils/FileUpload.js';
import DocumentController from '../controller/DocumentController.js';
import authJwt from '../middleware/authJwt.js';

const router = Router();
router.post(
  '/upload',
  authJwt,
  FileUpload.single('file'),
  DocumentController.upload,
);
router.get('/:userId', authJwt, DocumentController.getDocumentsByUserId);
router.get('/doc/:id', authJwt, DocumentController.getDocumentById);
router.delete('/doc/:id', authJwt, DocumentController.DeleteDocumentById);

const documentRoutes = router;
export default documentRoutes;
