import { Router } from 'express';
import AuthController from '../controller/AuthController.js'; // ✅ default import
import { signupValidate, loginValidate } from '../validators/AuthValidator.js';
import authJwt from '../middleware/authJwt.js';

const router = Router();

router.post('/signup', signupValidate, AuthController.signUp);
router.post('/login', loginValidate, AuthController.login);
router.get('/user/:id', authJwt, AuthController.getUser);

const authRoutes = router;
export default authRoutes;
