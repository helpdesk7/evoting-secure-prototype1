import type { Request, Response, NextFunction } from "express";

/** Require a scope on req.user.scopes; return 401/403 otherwise. */
export function requireScope(required: string) {
  return (req: Request, res: Response, next: NextFunction) => {
    const user: any = (req as any).user;
    if (!user) return res.status(401).json({ error: "unauthenticated" });
    if (!Array.isArray(user.scopes) || !user.scopes.includes(required)) {
      return res.status(403).json({ error: "insufficient_scope", required });
    }
    return next();
  };
}
