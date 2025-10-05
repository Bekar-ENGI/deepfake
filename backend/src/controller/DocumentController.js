import DocumentService from '../services/DocumentService.js';

class DocumentController {
  static async upload(req, res) {
    try {
      const { userId, username } = req.query; // or req.query if passed via query
      const file = req.file;

      if (!userId || !username) {
        return res
          .status(400)
          .json({ error: 'userId and username are required' });
      }

      const document = await DocumentService.uploadDocument(
        file,
        parseInt(userId),
        username,
      );

      res.status(201).json({
        success: true,
        message: 'Document uploaded successfully',
        data: document,
      });
    } catch (error) {
      console.error('Upload Error:', error.message);
      res.status(500).json({ error: error.message });
    }
  }

  static async getDocumentsByUserId(req, res) {
    try {
      const { userId } = req.params;
      if (!userId) {
        return res.json({
          success: false,
          message: 'userId is required',
        });
      }
      const documents = await DocumentService.getAllDocumentsByUserId(userId);
      res.json({
        success: true,
        message: 'Documents fetched successfully',
        data: documents,
      });
    } catch (error) {
      console.error('Get Documents Error:', error.message);
      return res.status(500).json({ error: error.message });
    }
  }

  static async getDocumentById(req, res) {
    try {
      const { id } = req.params;
      if (!id) {
        return res.json({
          success: false,
          message: 'id is required',
        });
      }
      const document = await DocumentService.getDocumentById(id);
      res.json({
        success: true,
        message: 'Document fetched successfully',
        data: document,
      });
    } catch (error) {
      console.error('Get Document Error:', error.message);
      return res.status(500).json({ error: error.message });
    }
  }

  static async DeleteDocumentById(req, res) {
    try {
      const { id } = req.params;
      if (!id) {
        return res.json({
          success: false,
          message: 'id is required',
        });
      }
      const document = await DocumentService.DeleteDocumentById(id);
      res.json({
        success: true,
        message: 'Document deleted successfully',
        data: document,
      });
    } catch (error) {
      console.error('Get Document Error:', error.message);
      return res.status(500).json({ error: error.message });
    }
  }
}

export default DocumentController;
