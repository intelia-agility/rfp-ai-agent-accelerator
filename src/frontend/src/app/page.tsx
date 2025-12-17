"use client";

import { useState } from "react";
import Image from "next/image";

// Helper to get API URL
const getApiUrl = () => {
  return process.env.NEXT_PUBLIC_API_URL || "https://rfp-backend-680149411946.australia-southeast2.run.app";
};

export default function Home() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [companyUrl, setCompanyUrl] = useState("https://www.intelia.com.au/");

  const [analyzing, setAnalyzing] = useState(false);
  const [drafting, setDrafting] = useState(false);

  const [result, setResult] = useState<any>(null);
  const [draftResult, setDraftResult] = useState<string>("");

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAssess = async () => {
    if (!file) return;

    setAnalyzing(true);
    setResult(null);
    setDraftResult("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${getApiUrl()}/assess`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Assessment failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error assessing RFP:", error);
      alert("Error assessing RFP. Please check backend connection.");
    } finally {
      setAnalyzing(false);
    }
  };

  const [draftUrl, setDraftUrl] = useState<string | null>(null);

  const handleDraft = async () => {
    if (!file) return;

    setDrafting(true);
    setDraftUrl(null);
    setDraftResult("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("company_url", companyUrl);

      const response = await fetch(`${getApiUrl()}/draft`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || "Drafting failed");
      }

      // Handle JSON Response (Google Drive Link)
      const data = await response.json();

      if (data.drive_url) {
        setDraftUrl(data.drive_url);
        setDraftResult(data.message || "Draft saved to Google Drive successfully.");
      } else {
        setDraftResult(data.message || "Draft generated but could not be uploaded to Drive.");
      }

    } catch (error: any) {
      console.error("Error drafting response:", error);
      alert(`Error: ${error.message}`);
    } finally {
      setDrafting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-100 dark:bg-[#0a0a0a] dark:text-slate-100">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 px-6 py-4 backdrop-blur-md dark:border-white/10 dark:bg-black/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-lg shadow-lg flex items-center justify-center text-white font-bold">
              R
            </div>
            <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
              RFP<span className="text-blue-600">Accelerator</span>
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button className="text-sm font-medium text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">
              History
            </button>
            <button className="text-sm font-medium text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">
              Settings
            </button>
            <div className="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-800"></div>
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-7xl px-6 py-12">
        {/* Header Section */}
        <div className="mb-16 text-center">
          <h1 className="mb-4 text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white md:text-6xl">
            Automate your <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">RFP Response</span>
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-slate-600 dark:text-slate-400">
            Upload your RFP documents and let our AI agent analyze, score, and draft a winning response in seconds.
          </p>
        </div>

        {/* Main Grid */}
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Left Column: Upload */}
          <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xl dark:border-white/10 dark:bg-slate-900/50 dark:shadow-2xl">
            <div className="p-8">
              <h2 className="mb-6 text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <svg
                  className="h-6 w-6 text-blue-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                Document Upload
              </h2>

              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative flex min-h-[240px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed transition-all duration-200 ${isDragging
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-slate-300 hover:border-slate-400 dark:border-slate-700 dark:hover:border-slate-600"
                  }`}
              >
                <input
                  type="file"
                  className="absolute inset-0 z-10 opacity-0 cursor-pointer"
                  onChange={handleFileChange}
                />
                <div className="text-center">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
                    <svg
                      className="h-8 w-8 text-slate-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                  </div>
                  {file ? (
                    <div className="px-4">
                      <p className="text-lg font-semibold text-slate-900 dark:text-white">
                        {file.name}
                      </p>
                      <p className="text-sm text-slate-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  ) : (
                    <>
                      <p className="mb-2 text-lg font-medium text-slate-900 dark:text-white">
                        Drop your file here, or click to browse
                      </p>
                      <p className="text-sm text-slate-500">
                        PDF, DOCX, or TXT
                      </p>
                    </>
                  )}
                </div>
              </div>

              {/* Company URL Input */}
              <div className="mt-6">
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Company Knowledge Base URL</label>
                <input
                  type="url"
                  value={companyUrl}
                  onChange={(e) => setCompanyUrl(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:border-blue-500"
                  placeholder="https://www.company.com"
                />
              </div>

              <div className="mt-6">
                <button
                  onClick={handleAssess}
                  disabled={!file || analyzing}
                  className={`w-full rounded-xl py-4 text-base font-bold shadow-lg transition-all duration-200 ${!file
                    ? "bg-slate-200 text-slate-400 cursor-not-allowed dark:bg-slate-800 dark:text-slate-600"
                    : "bg-blue-600 text-white hover:bg-blue-700 hover:shadow-blue-500/25 active:scale-[0.98]"
                    }`}
                >
                  {analyzing ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg
                        className="h-5 w-5 animate-spin"
                        viewBox="0 0 24 24"
                      >
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
                      Analyzing Document...
                    </span>
                  ) : (
                    "Process RFP"
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: Results */}
          <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xl dark:border-white/10 dark:bg-slate-900/50 dark:shadow-2xl">
            <div className="p-8 h-full flex flex-col">
              <h2 className="mb-6 text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Analysis Results
              </h2>

              {!result ? (
                <div className="flex flex-1 items-center justify-center flex-col text-center opacity-50">
                  <div className="mb-4 h-24 w-24 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                    <svg className="h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                  </div>
                  <p className="text-lg text-slate-500">
                    Results will appear here after analysis
                  </p>
                </div>
              ) : (
                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                  {/* Top Score Cards */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="rounded-2xl bg-slate-50 p-6 dark:bg-white/5">
                      <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Recommendation</p>
                      <p className={`mt-2 text-3xl font-bold ${result.recommendation === "Pursue" ? "text-green-500" : "text-red-500"}`}>
                        {result.recommendation}
                      </p>
                    </div>
                    <div className="rounded-2xl bg-slate-50 p-6 dark:bg-white/5">
                      <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Total Score</p>
                      <div className="mt-2 flex items-baseline gap-1">
                        <span className="text-3xl font-bold text-slate-900 dark:text-white">{result.score}</span>
                        <span className="text-sm text-slate-500">/100</span>
                      </div>
                    </div>
                  </div>

                  {/* Criteria Progress Bars */}
                  <div className="space-y-2">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">Criteria</h3>
                    {Object.entries(result.criteria_scores).map(([key, score]: [string, any]) => (
                      <div key={key} className="group">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="capitalize font-medium text-slate-700 dark:text-slate-200">{key}</span>
                          <span className="font-bold text-slate-900 dark:text-white">{score}%</span>
                        </div>
                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                          <div
                            className="h-full bg-blue-600"
                            style={{ width: `${score}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Reasoning */}
                  <div className="rounded-xl border border-blue-100 bg-blue-50 p-4 dark:border-blue-900/30 dark:bg-blue-900/20">
                    <h3 className="mb-1 text-sm font-semibold text-blue-900 dark:text-blue-100">Analysis</h3>
                    <p className="text-sm leading-relaxed text-blue-800 dark:text-blue-200">
                      {result.reasoning}
                    </p>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col gap-3 pt-2">
                    <button
                      onClick={handleDraft}
                      disabled={drafting}
                      className="flex items-center justify-center gap-2 rounded-xl bg-slate-900 py-3 text-sm font-semibold text-white shadow-lg hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100"
                    >
                      {drafting ? "Generating Draft..." : "Draft Response"}
                    </button>

                    {draftResult && (
                      <div className="mt-4 p-4 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                        <p className="text-sm font-medium mb-3">{draftResult}</p>

                        {draftUrl && (
                          <a
                            href={draftUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                            Open in Google Drive
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
