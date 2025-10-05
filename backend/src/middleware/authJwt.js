import jwt from 'jsonwebtoken';
import ApiError from '../utils/ApiError.js';

const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) throw new Error('JWT_SECRET is not defined');

export default function authJwt(req, res, next) {
  const authHeader =
    req.headers['authorization'] || req.headers['Authorization'];

  if (!authHeader || !authHeader.toLowerCase().startsWith('bearer ')) {
    return next(new ApiError(401, 'No Token Provided'));
  }

  const token = authHeader.split(' ')[1];

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = { id: payload.sub, email: payload.email };
    next();
  } catch (error) {
    next(new ApiError(401, 'Invalid or Expired Token'));
  }
}
