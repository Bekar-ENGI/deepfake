import AuthService from '../services/AuthService.js';

async function signUp(req, res, next) {
  try {
    const result = await AuthService.signUp(req.body);
    res
      .status(201)
      .json({
        success: true,
        message: 'User Created Successfully',
        data: result,
      });
  } catch (error) {
    next(error);
  }
}

async function login(req, res, next) {
  try {
    const result = await AuthService.login(req.body);
    res
      .status(200)
      .json({
        success: true,
        message: 'User Logged In Successfully',
        data: result,
      });
  } catch (error) {
    next(error);
  }
}

async function getUser(req, res, next) {
  try {
    const { id } = req.params;
    const result = await AuthService.getUserById(id);
    res
      .status(200)
      .json({
        success: true,
        message: 'User Found Successfully',
        data: result,
      });
  } catch (error) {
    next(error);
  }
}

export default { signUp, login, getUser };
