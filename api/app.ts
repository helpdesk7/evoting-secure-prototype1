import "dotenv/config";
import express, { Request, Response } from "express";
import { resultsRouter } from "./routes/results";

const app = express();
app.use(express.json());

app.use("/results", resultsRouter);

app.get("/healthz", (_req: Request, res: Response) => {
  res.status(200).json({ status: "ok" });
});

const PORT = process.env.PORT || 8004;
app.listen(PORT, () => {
  console.log(`✅ Results API listening on port ${PORT}`);
});
