// The only file that knows backend URLs. Every path starts with /api, which the proxy routes to a service.

export interface DocumentItem {
  id: number;
  title: string;
  content: string;
  created_at: string;
}

export interface SourceRef {
  id: number;
  title: string;
}

export interface ChatAnswer {
  answer: string;
  sources: SourceRef[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    throw new Error(`${init?.method ?? "GET"} ${path} failed with ${response.status}`);
  }
  return (await response.json()) as T;
}

export function listDocuments(): Promise<DocumentItem[]> {
  return request<DocumentItem[]>("/api/documents/");
}

export function createDocument(title: string, content: string): Promise<DocumentItem> {
  return request<DocumentItem>("/api/documents/", {
    method: "POST",
    body: JSON.stringify({ title, content }),
  });
}

export function askQuestion(question: string): Promise<ChatAnswer> {
  return request<ChatAnswer>("/api/chat/ask", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}
