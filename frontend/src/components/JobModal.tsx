"use client";

import { useState, useRef, useEffect } from "react";
import { Job, ResumeAnalysisResponse } from "@/types";
import { analyzeResume, getJob } from "@/lib/api";
import ResumeAnalysis from "./ResumeAnalysis";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

interface JobModalProps {
  job: Job | null;
  open: boolean;
  onClose: () => void;
}

export default function JobModal({ job, open, onClose }: JobModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<ResumeAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fullJob, setFullJob] = useState<Job | null>(null);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setAnalysis(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile || !job) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await analyzeResume(job.id, selectedFile);
      setAnalysis(result);
    } catch {
      setError("Failed to analyze resume. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const loadJobDetails = async () => {
    if (!job || fullJob?.id === job.id) return;

    setIsLoadingDetails(true);
    try {
      const details = await getJob(job.id);
      setFullJob(details);
    } catch {
      // Keep using the partial job data
    } finally {
      setIsLoadingDetails(false);
    }
  };

  // Load details when modal opens
  useEffect(() => {
    if (open && job) {
      loadJobDetails();
      // Reset state when opening new job
      setSelectedFile(null);
      setAnalysis(null);
      setError(null);
    }
  }, [open, job?.id]);

  if (!job) return null;

  const displayJob = fullJob?.id === job.id ? fullJob : job;

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-3xl max-h-[90vh] p-0 gap-0">
        <DialogHeader className="px-6 py-4 border-b">
          <DialogTitle className="text-xl font-semibold pr-8">
            {displayJob.title}
          </DialogTitle>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-muted-foreground font-medium">
              {displayJob.company}
            </span>
            {displayJob.location && (
              <>
                <span className="text-muted-foreground">•</span>
                <span className="text-muted-foreground text-sm flex items-center gap-1">
                  <svg
                    className="w-3.5 h-3.5"
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
                  {displayJob.location}
                </span>
              </>
            )}
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            <Badge variant="secondary">{displayJob.platform}</Badge>
            {displayJob.job_type && (
              <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                {displayJob.job_type}
              </Badge>
            )}
            {displayJob.salary_range && (
              <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
                {displayJob.salary_range}
              </Badge>
            )}
            {displayJob.posted_date && (
              <Badge variant="outline">
                {displayJob.posted_date}
              </Badge>
            )}
          </div>
        </DialogHeader>

        <ScrollArea className="flex-1 max-h-[calc(90vh-180px)]">
          <div className="p-6 space-y-6">
            {/* View on platform link */}
            <a
              href={displayJob.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-sm text-primary hover:underline font-medium"
            >
              View on {displayJob.platform}
              <svg
                className="w-3.5 h-3.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
            </a>

            {/* Job Description */}
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-2 uppercase tracking-wide">
                Job Description
              </h3>
              {isLoadingDetails ? (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Loading description...
                </div>
              ) : displayJob.description ? (
                <div className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
                  {displayJob.description}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground italic">
                  Description not available. Click the link above to see the full job posting.
                </p>
              )}
            </div>

            {/* Resume Upload Section */}
            <div className="border-t pt-6">
              <h3 className="text-sm font-semibold text-foreground mb-1 uppercase tracking-wide">
                Resume Match Analysis
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                Upload your resume to see how well it matches this job.
              </p>

              <div className="space-y-4">
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-border rounded-lg p-5 text-center cursor-pointer hover:border-primary/50 hover:bg-muted/50 transition-colors"
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  {selectedFile ? (
                    <div className="flex items-center justify-center gap-2">
                      <svg
                        className="w-6 h-6 text-green-500"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <span className="text-sm font-medium">{selectedFile.name}</span>
                    </div>
                  ) : (
                    <>
                      <svg
                        className="mx-auto h-10 w-10 text-muted-foreground/50"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={1.5}
                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                      </svg>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Click to upload your resume
                      </p>
                      <p className="text-xs text-muted-foreground/70">
                        PDF, DOC, DOCX, or TXT
                      </p>
                    </>
                  )}
                </div>

                <Button
                  onClick={handleAnalyze}
                  disabled={!selectedFile || isAnalyzing}
                  className="w-full"
                  size="lg"
                >
                  {isAnalyzing ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                          fill="none"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                      Analyzing...
                    </span>
                  ) : (
                    "Analyze My Resume"
                  )}
                </Button>

                {error && (
                  <p className="text-destructive text-sm text-center">{error}</p>
                )}
              </div>
            </div>

            {/* Analysis Results */}
            {analysis && (
              <div className="border-t pt-6">
                <h3 className="text-sm font-semibold text-foreground mb-4 uppercase tracking-wide">
                  Analysis Results
                </h3>
                <ResumeAnalysis analysis={analysis} />
              </div>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
