import { hash, compare } from 'bcryptjs'; // Using bcryptjs for cross-platform compatibility
const SALT_ROUNDS = 10;

async function hashPassword(plain) {
  return await hash(plain, SALT_ROUNDS);
}

async function comparePassword(plain, hashedPassword) {
  return await compare(plain, hashedPassword);
}

export { hashPassword, comparePassword };
