import prisma from '../config/db.js';

async function connectDb() {
  try {
    await prisma.$connect();
    console.log('Database Connected');
  } catch (error) {
    console.error('Prisma Connection Error', error);
    throw error;
  }
}

const shutdown = async () => {
  try {
    await prisma.$disconnect();
    console.log('Database Disconnected');
    process.exit(0);
  } catch (error) {
    process.exit(1);
  }
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

export default connectDb;
