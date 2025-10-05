import { forwardFile } from '../api/service/FileService.js';
import prisma from '../config/db.js';

class DocumentService {
  /**
   * Upload a document and save record in DB
   * @param {Object} file - multer file object
   * @param {number} userId
   * @param {string} username
   * @returns {Object} saved document record
   */
  static async uploadDocument(file, userId, username) {
    if (!file) {
      throw new Error('File is required');
    }

    // Forward the file to FastAPI backend
    const response = await forwardFile(file, userId, username);

    // Get the filename returned by FastAPI
    const storedFilename = response.data?.file_name;
    if (!storedFilename) {
      throw new Error('Filename not returned from backend');
    }

    // Save document record in Prisma
    const document = await prisma.document.create({
      data: {
        userId: userId,
        filename: storedFilename,
        filetype: file.mimetype,
        uploadedAt: new Date(), // optional, Prisma default is now()
      },
    });

    return document;
  }

  static async getAllDocumentsByUserId(userId) {
    const docs = await prisma.document.findMany({
      where: {
        userId: parseInt(userId, 10),
      },
    });
    return docs;
  }

  static async getDocumentById(id) {
    const doc = await prisma.document.findUnique({
      where: {
        id: parseInt(id, 10),
      },
    });
    return doc;
  }

  static async DeleteDocumentById(id) {
    const doc = prisma.document.delete({
      where: {
        id: parseInt(id, 10),
      },
    });
    return doc;
  }
}

export default DocumentService;
