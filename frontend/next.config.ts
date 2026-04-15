import type { NextConfig } from "next";

function extractHostFromUrl(candidate: string | undefined): string | null {
  if (!candidate) {
    return null;
  }
  try {
    const url = new URL(candidate);
    return url.hostname;
  } catch {
    return null;
  }
}

const allowedDevOrigins = Array.from(
  new Set(
    [
      "localhost",
      "127.0.0.1",
      extractHostFromUrl(process.env.NEXT_PUBLIC_MOBILE_APP_URL),
      extractHostFromUrl(process.env.NEXT_PUBLIC_API_BASE_URL),
    ].filter((value): value is string => Boolean(value))
  )
);

const nextConfig: NextConfig = {
  allowedDevOrigins,
};

export default nextConfig;
