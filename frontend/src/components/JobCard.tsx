"use client";

import { Job } from "@/types";

interface JobCardProps {
  job: Job;
  onClick: () => void;
}

export default function JobCard({ job, onClick }: JobCardProps) {
  const platformColors: Record<string, string> = {
    linkedin: "bg-blue-100 text-blue-800",
    glassdoor: "bg-green-100 text-green-800",
  };

  const jobTypeColors: Record<string, string> = {
    remote: "bg-purple-100 text-purple-800",
    onsite: "bg-orange-100 text-orange-800",
    hybrid: "bg-teal-100 text-teal-800",
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow-md p-5 cursor-pointer hover:shadow-lg transition-shadow border border-gray-100"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
          {job.title}
        </h3>
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            platformColors[job.platform] || "bg-gray-100 text-gray-800"
          }`}
        >
          {job.platform}
        </span>
      </div>

      <p className="text-gray-700 font-medium mb-2">{job.company}</p>

      {job.location && (
        <p className="text-gray-500 text-sm mb-2 flex items-center gap-1">
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          {job.location}
        </p>
      )}

      <div className="flex flex-wrap gap-2 mt-3">
        {job.job_type && (
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${
              jobTypeColors[job.job_type] || "bg-gray-100 text-gray-800"
            }`}
          >
            {job.job_type}
          </span>
        )}

        {job.salary_range && (
          <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            {job.salary_range}
          </span>
        )}

        {job.posted_date && (
          <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
            {job.posted_date}
          </span>
        )}
      </div>
    </div>
  );
}
