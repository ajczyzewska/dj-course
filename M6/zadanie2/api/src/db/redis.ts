import Redis from "ioredis";

const redis = new Redis(process.env.REDIS_URL || "redis://localhost:6379");

redis.on("connect", () => console.log("Connected to Redis"));
redis.on("error", (err) => console.error("Redis error:", err));

export async function getCache<T>(key: string): Promise<T | null> {
  const data = await redis.get(key);
  if (!data) return null;
  return JSON.parse(data) as T;
}

export async function setCache(key: string, data: unknown, ttl = 60): Promise<void> {
  await redis.set(key, JSON.stringify(data), "EX", ttl);
}

export async function invalidateCache(key: string): Promise<void> {
  await redis.del(key);
}

export default redis;
