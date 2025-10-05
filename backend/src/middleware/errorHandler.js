export default (err, req, res, next) => {
  const status = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';
  const details = err.details || null;

  console.error(err);

  res.status(status).json({
    success: false,
    message,
    details
  });
};
