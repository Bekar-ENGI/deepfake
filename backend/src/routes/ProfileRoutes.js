import { Router } from 'express';
import upload from '../utils/upload.js';
import ProfileController from '../controller/ProfileController.js';
import authJwt from '../middleware/authJwt.js';

const router = Router();

router.post(
  `/:userId/profile`,
  upload.single(`image`),
  authJwt,
  ProfileController.uploadProfileImage,
);
router.get(`/:userId/profile`, authJwt, ProfileController.getImage);

const profileRoutes = router;
export default profileRoutes;
