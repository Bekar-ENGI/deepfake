import FormData from 'form-data';
import axiosClient from '../lib/axiosClient.js';

export async function forwardFile(file, userId, username) {
  try {
    if (!file) throw new Error('File is required');
    if (!userId || !username)
      throw new Error('userId and username are required');

    // Ensure userId is a number
    const numericUserId = Number(userId);
    if (isNaN(numericUserId)) throw new Error('Invalid userId');

    const form = new FormData();
    form.append('file', file.buffer, file.originalname);

    // Relative URL; Axios prepends baseURL
    const url = `/document/upload?userId=${numericUserId}&username=${encodeURIComponent(username)}&max_words=450`;

    const response = await axiosClient.post(url, form, {
      headers: {
        ...form.getHeaders(), // sets multipart/form-data correctly
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error forwarding file:', error.message);
    throw error;
  }
}
