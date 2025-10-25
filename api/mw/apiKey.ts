import type { Request, Response, NextFunction } from "express";

/** Simple API-key auth via env RESULTS_API_KEY for coursework. */
export function apiKeyAuth(req: Request, res: Response, next: NextFunction) {
  const supplied = req.header("x-api-key") || "";
  const expected = process.env.RESULTS_API_KEY || "";
  if (!expected) return res.status(500).json({ error: "server_misconfigured: RESULTS_API_KEY missing" });
  if (!supplied)  return res.status(401).json({ error: "missing api key" });
  if (supplied !== expected) return res.status(403).json({ error: "invalid api key" });
  return next();
}
