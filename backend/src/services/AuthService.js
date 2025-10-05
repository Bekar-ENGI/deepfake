import prisma from '../config/db.js';
import { hashPassword, comparePassword } from '../utils/hash.js';
import ApiError from '../utils/ApiError.js';
import jwt from 'jsonwebtoken';

const { sign } = jwt;

const JWT_SECRET = process.env.JWT_SECRET;
const JWT_EXPIRE = process.env.JWT_EXPIRE || '7d';
if (!JWT_SECRET) throw new Error('JWT_SECRET is not defined');

async function signUp({ email, password, name }) {
  if (!email || !password)
    throw new ApiError(400, 'Email and Password are required');

  const existing = await prisma.user.findUnique({ where: { email } });
  if (existing) throw new ApiError(409, 'User Already Exists With This Email');

  const hashed = await hashPassword(password);
  const user = await prisma.user.create({
    data: { email, password: hashed, name },
  });

  return {
    id: user.id,
    email: user.email,
    name: user.name,
    createdAt: user.createdAt,
  };
}

async function login({ email, password }) {
  if (!email || !password)
    throw new ApiError(400, 'Email and Password are required');

  const user = await prisma.user.findUnique({ where: { email } });
  if (!user) throw new ApiError(401, 'Invalid Credentials');

  const valid = await comparePassword(password, user.password);
  if (!valid) throw new ApiError(401, 'Invalid Credentials');

  const token = sign(
    { sub: user.id.toString(), email: user.email },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRE },
  );
  return { token, user: { id: user.id, email: user.email, name: user.name } };
}

async function getUserById(id) {
  const user = await prisma.user.findUnique({
    where: { id: parseInt(id, 10) },
  });
  if (!user) throw new ApiError(404, 'User Not Found');

  return {
    id: user.id,
    email: user.email,
    name: user.name,
    createdAt: user.createdAt,
    updatedAt: user.updatedAt,
  };
}

export default { signUp, login, getUserById };
