import { useAuth } from "@clerk/nextjs";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchApi(
  endpoint: string,
  options: RequestInit = {},
  token?: string
) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

export interface Memory {
  memory_id: string;
  user_id: string;
  memory_type: string;
  content: string;
  entities: string[];
  attributes: Record<string, any>;
  confidence: number;
  created_at: string;
  updated_at: string;
  access_count: number;
  last_accessed: string | null;
}

export interface MemoryListResponse {
  memories: Memory[];
  total: number;
  page: number;
  page_size: number;
}

export async function listMemories(
  token: string,
  page: number = 1,
  pageSize: number = 20
): Promise<MemoryListResponse> {
  return fetchApi(
    `/v1/memories/list?page=${page}&page_size=${pageSize}`,
    { method: "GET" },
    token
  );
}

export async function searchMemories(
  token: string,
  query: string,
  k: number = 5
): Promise<{ memories: Memory[]; query: string }> {
  return fetchApi(
    "/v1/memories/retrieve",
    {
      method: "POST",
      body: JSON.stringify({ query, k }),
    },
    token
  );
}

export async function deleteMemory(
  token: string,
  memoryId: string
): Promise<{ success: boolean; message: string }> {
  return fetchApi(
    `/v1/memories/${memoryId}`,
    { method: "DELETE" },
    token
  );
}

export interface HealthStatus {
  status: string;
  database: string;
  cache: string;
  vector_db: string;
  version: string;
}

export async function getHealthStatus(token?: string): Promise<HealthStatus> {
  return fetchApi("/health/detailed", { method: "GET" }, token);
}
