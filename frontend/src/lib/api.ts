import {
  JobSearchRequest,
  JobSearchResponse,
  Job,
  ResumeAnalysisResponse,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchJobs(
  request: JobSearchRequest
): Promise<JobSearchResponse> {
  const response = await fetch(`${API_BASE}/api/jobs/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error("Failed to search jobs");
  }

  return response.json();
}

export type StreamEvent =
  | { type: "start"; platforms: string[] }
  | { type: "jobs"; platform: string; jobs: Job[]; count: number }
  | { type: "done" }
  | { type: "error"; message: string };

export async function searchJobsStream(
  request: JobSearchRequest,
  onEvent: (event: StreamEvent) => void
): Promise<void> {
  const response = await fetch(`${API_BASE}/api/jobs/search/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error("Failed to search jobs");
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Process complete SSE messages
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          onEvent(data);
        } catch {
          console.error("Failed to parse SSE data:", line);
        }
      }
    }
  }
}

export async function getJob(jobId: string): Promise<Job> {
  const response = await fetch(`${API_BASE}/api/jobs/${jobId}`);

  if (!response.ok) {
    throw new Error("Failed to get job");
  }

  return response.json();
}

export async function analyzeResume(
  jobId: string,
  resume: File
): Promise<ResumeAnalysisResponse> {
  const formData = new FormData();
  formData.append("job_id", jobId);
  formData.append("resume", resume);

  const response = await fetch(`${API_BASE}/api/analysis/match`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to analyze resume");
  }

  return response.json();
}
