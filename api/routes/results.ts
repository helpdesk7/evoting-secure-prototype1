import { Router, Request, Response, NextFunction } from "express";
import { sha256Hex } from "../services/checksum";
import { resultsLimiter } from "../mw/rateLimit";
import { apiKeyAuth } from "../mw/apiKey";
import { requireScope } from "../mw/scope";

export const resultsRouter = Router();

/** Allow EITHER x-api-key OR (future) Bearer with scope results:read */
function combinedAuth(req: Request, res: Response, next: NextFunction) {
  const hasApiKey = !!req.header("x-api-key");
  const hasBearer = (req.header("authorization") || "").toLowerCase().startsWith("bearer ");
  if (!hasApiKey && !hasBearer) return res.status(401).json({ error: "missing credentials" });
  if (hasApiKey) return apiKeyAuth(req, res, next);
  // TODO: plug bearerAuth, then:
  // return bearerAuth(req, res, () => requireScope("results:read")(req, res, next));
  return requireScope("results:read")(req, res, next);
}

resultsRouter.get("/:electionId", resultsLimiter, combinedAuth, async (req: Request, res: Response) => {
  const { electionId } = req.params;

  // TODO: replace with real tallied results
  const payload = {
    electionId,
    generatedAt: new Date().toISOString(),
    totals: [
      { candidateId: "cand-1", votes: 1234 },
      { candidateId: "cand-2", votes: 987 }
    ]
  };

  const body = Buffer.from(JSON.stringify(payload));
  const hex = sha256Hex(body);
  res.setHeader("Content-Type", "application/json");
  res.setHeader("X-Content-Checksum", `sha256=${hex}`);
  res.status(200).send(body);
});
