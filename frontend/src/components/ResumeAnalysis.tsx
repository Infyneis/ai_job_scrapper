"use client";

import { ResumeAnalysisResponse } from "@/types";

interface ResumeAnalysisProps {
  analysis: ResumeAnalysisResponse;
}

export default function ResumeAnalysis({ analysis }: ResumeAnalysisProps) {
  const getMatchColor = (percentage: number) => {
    if (percentage >= 70) return "text-green-600";
    if (percentage >= 50) return "text-yellow-600";
    return "text-red-600";
  };

  const getMatchBgColor = (percentage: number) => {
    if (percentage >= 70) return "bg-green-500";
    if (percentage >= 50) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className="space-y-6">
      {/* Match Percentage */}
      <div className="text-center">
        <div className="relative inline-flex items-center justify-center w-32 h-32">
          <svg className="w-32 h-32 transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              className="text-gray-200"
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${(analysis.match_percentage / 100) * 352} 352`}
              className={getMatchBgColor(analysis.match_percentage)}
              strokeLinecap="round"
            />
          </svg>
          <span
            className={`absolute text-3xl font-bold ${getMatchColor(
              analysis.match_percentage
            )}`}
          >
            {analysis.match_percentage}%
          </span>
        </div>
        <p className="mt-2 text-gray-600 font-medium">Match Score</p>
      </div>

      {/* Matching Skills */}
      {analysis.matching_skills.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <svg
              className="w-5 h-5 text-green-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            Matching Skills
          </h4>
          <div className="flex flex-wrap gap-2">
            {analysis.matching_skills.map((skill, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Missing Skills */}
      {analysis.missing_skills.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <svg
              className="w-5 h-5 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
            Skills to Develop
          </h4>
          <div className="flex flex-wrap gap-2">
            {analysis.missing_skills.map((skill, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <svg
              className="w-5 h-5 text-blue-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Recommendations
          </h4>
          <ul className="space-y-2">
            {analysis.recommendations.map((rec, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-sm text-gray-600"
              >
                <span className="text-blue-500 mt-1">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
