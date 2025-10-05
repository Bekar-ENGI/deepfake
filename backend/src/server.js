import createApp from './app.js';
import connectDb from './loaders/dbloader.js';

const PORT = process.env.PORT || 4000;

async function start() {
  try {
    await connectDb();
    const app = createApp();
    app.listen(PORT, () => console.log(`Server is running on port ${PORT}`));
  } catch (error) {
    console.error('Error Starting Server', error);
    process.exit(1);
  }
}

start();
