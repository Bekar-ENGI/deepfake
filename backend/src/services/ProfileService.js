import prisma from '../config/db.js';

class ProfileService {
  static async uploadProfileImage(userId, fileBuffer) {
    const userIdInt = parseInt(userId, 10);

    return await prisma.profile.upsert({
      where: { userId: userIdInt },
      update: { image: fileBuffer, uploadedAt: new Date() },
      create: { userId: userIdInt, image: fileBuffer, uploadedAt: new Date() },
    });
  }

  static async getProfileImage(userId) {
    const userIdInt = parseInt(userId, 10);

    return await prisma.profile.findUnique({
      where: { userId: userIdInt },
      select: { image: true },
    });
  }
}

export default ProfileService;
