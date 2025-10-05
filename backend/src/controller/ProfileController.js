import ProfileService from '../services/ProfileService.js';

class ProfileController {
  static async uploadProfileImage(req, res) {
    try {
      const { userId } = req.params;
      if (!req.file) {
        return res.status(400).json({
          success: false,
          message: 'Image is required',
        });
      }
      const profile = await ProfileService.uploadProfileImage(
        userId,
        req.file.buffer,
      );
      return res.status(200).json({
        success: true,
        message: 'Image uploaded successfully',
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Internal Server Error',
        details: error.message,
      });
    }
  }
  static async getImage(req, res) {
    try {
      const { userId } = req.params;
      const profile = await ProfileService.getProfileImage(userId);

      if (!profile || !profile.image) {
        return res.status(404).json({ error: 'Image not found' });
      }
      //   TODO: Set the correct content type
      res.set('Content-Type', 'image/jpeg'); // or detect mime type dynamically
      res.send(profile.image);
    } catch (error) {
      console.error(error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}

export default ProfileController;
