"use client";

import { useState } from "react";
import SearchFilters from "@/components/SearchFilters";
import JobList from "@/components/JobList";
import JobModal from "@/components/JobModal";
import { searchJobsStream, StreamEvent } from "@/lib/api";
import { Job, JobType, Platform } from "@/types";

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingPlatforms, setLoadingPlatforms] = useState<string[]>([]);
  const [completedPlatforms, setCompletedPlatforms] = useState<string[]>([]);

  const handleSearch = async (filters: {
    query: string;
    location: string;
    job_type: JobType;
    platforms: Platform[];
  }) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    setJobs([]);
    setLoadingPlatforms([]);
    setCompletedPlatforms([]);

    try {
      await searchJobsStream(
        {
          query: filters.query,
          location: filters.location || undefined,
          job_type: filters.job_type,
          platforms: filters.platforms,
        },
        (event: StreamEvent) => {
          switch (event.type) {
            case "start":
              setLoadingPlatforms(event.platforms);
              break;
            case "jobs":
              setJobs((prev) => [...prev, ...event.jobs]);
              setLoadingPlatforms((prev) =>
                prev.filter((p) => p !== event.platform)
              );
              setCompletedPlatforms((prev) => [...prev, event.platform]);
              break;
            case "done":
              setIsLoading(false);
              setLoadingPlatforms([]);
              break;
            case "error":
              setError(event.message);
              setIsLoading(false);
              break;
          }
        }
      );
    } catch (err) {
      setError("Failed to search jobs. Please make sure the backend is running.");
      setJobs([]);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Job Scraper</h1>
          <p className="text-gray-600 mt-1">
            Search jobs from LinkedIn and Glassdoor with AI-powered resume matching
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Search Filters */}
        <SearchFilters onSearch={handleSearch} isLoading={isLoading} />

        {/* Error Message */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Loading Status */}
        {(loadingPlatforms.length > 0 || completedPlatforms.length > 0) && (
          <div className="mt-6 flex flex-wrap gap-3">
            {completedPlatforms.map((platform) => (
              <span
                key={platform}
                className="inline-flex items-center gap-2 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                {platform} done
              </span>
            ))}
            {loadingPlatforms.map((platform) => (
              <span
                key={platform}
                className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Searching {platform}...
              </span>
            ))}
          </div>
        )}

        {/* Results */}
        <div className="mt-8">
          {hasSearched ? (
            <JobList
              jobs={jobs}
              onSelectJob={setSelectedJob}
              isLoading={isLoading && jobs.length === 0}
            />
          ) : (
            <div className="text-center py-16">
              <svg
                className="mx-auto h-20 w-20 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
              <h2 className="mt-4 text-xl font-medium text-gray-900">
                Start Your Job Search
              </h2>
              <p className="mt-2 text-gray-500">
                Enter a job title and location to find opportunities from LinkedIn
                and Glassdoor
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Job Modal */}
      <JobModal
        job={selectedJob}
        open={!!selectedJob}
        onClose={() => setSelectedJob(null)}
      />
    </div>
  );
}
