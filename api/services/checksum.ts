import crypto from "crypto";
export function sha256Hex(data: Buffer | string): string {
  const buf = Buffer.isBuffer(data) ? data : Buffer.from(data, "utf8");
  return crypto.createHash("sha256").update(buf).digest("hex");
}
