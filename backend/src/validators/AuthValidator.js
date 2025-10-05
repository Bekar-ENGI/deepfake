import Joi from 'joi'; // ✅ import default

const SignUpSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(6).required(),
  name: Joi.string().max(100).optional(),
});

const LoginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required(),
});

function validate(schema) {
  return (req, res, next) => {
    const { error } = schema.validate(req.body, { abortEarly: false });
    if (error) {
      return res.status(400).json({
        statusCode: 400,
        message: 'Validation Error',
        details: error.details,
      });
    }
    next();
  };
}

export const signupValidate = validate(SignUpSchema);
export const loginValidate = validate(LoginSchema);
