export type JobType = "remote" | "onsite" | "hybrid" | "all";

export type Platform = "linkedin" | "glassdoor";

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string | null;
  job_type: string | null;
  salary_range: string | null;
  description: string | null;
  url: string;
  platform: string;
  posted_date: string | null;
}

export interface JobSearchRequest {
  query: string;
  location?: string;
  job_type: JobType;
  salary_min?: number;
  salary_max?: number;
  platforms: Platform[];
}

export interface JobSearchResponse {
  jobs: Job[];
  total: number;
}

export interface ResumeAnalysisResponse {
  match_percentage: number;
  matching_skills: string[];
  missing_skills: string[];
  recommendations: string[];
}
