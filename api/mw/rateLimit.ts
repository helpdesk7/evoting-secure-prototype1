import rateLimit from "express-rate-limit";

/** 60 req/min per IP for results endpoint */
export const resultsLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 60,
  standardHeaders: true,
  legacyHeaders: false
});
