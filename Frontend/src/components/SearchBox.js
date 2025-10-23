"use client";

import { useState } from "react";
import axios from "axios";
import { FiSearch } from "react-icons/fi";

export default function SearchBox() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("hybrid");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const sampleQueries = [
    "Similarity Search",
    "Testing",
    "Database",
    "Performance",
    "Cloud",
    "Security",
    "Optimization",
    "Machine Learning",
  ];

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await axios.post(
        `${API_URL}/search`,
        { query, mode },
        {
          timeout: 30000,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (res.data.results) {
        setResults(res.data.results);
      } else if (Array.isArray(res.data)) {
        setResults(res.data);
      } else {
        setResults([]);
      }
    } catch (err) {
      console.error("Search error:", err);

      let errorMessage = "Search failed. Please try again.";

      if (err.response) {
        errorMessage =
          err.response.data?.detail || `Server error: ${err.response.status}`;
      } else if (err.request) {
        errorMessage =
          "Cannot reach the server. Please check if the backend is running.";
      } else {
        errorMessage = err.message;
      }

      setError(errorMessage);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto mt-16 p-8 bg-gradient-to-br from-white via-gray-50 to-blue-50 shadow-lg rounded-3xl border border-gray-200">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-extrabold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
          Lexomat Intelligence Hybrid Search
        </h1>
        <p className="text-gray-600 mt-2">
          Experience <span className="font-medium text-blue-700">Keyword</span>,{" "}
          <span className="font-medium text-indigo-700">Semantic</span>, and{" "}
          <span className="font-medium text-purple-700">Hybrid</span> search in
          one unified interface.
        </p>

        <p className="text-xs text-gray-400 mt-2">Connected to: {API_URL}</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <div className="flex flex-1 items-center bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden focus-within:ring-2 focus-within:ring-blue-500">
          <FiSearch className="ml-3 text-gray-400" size={22} />
          <input
            type="text"
            placeholder="Search your dataset..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
            className="flex-1 p-3 outline-none text-gray-700 text-base bg-transparent"
          />
        </div>

        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className="p-3 rounded-xl bg-gray-100 text-gray-800 font-medium border border-gray-300 focus:ring-2 focus:ring-blue-500 shadow-sm transition-all">
          <option value="keyword">Keyword</option>
          <option value="semantic">Semantic</option>
          <option value="hybrid">Hybrid</option>
        </select>

        <button
          onClick={handleSearch}
          disabled={loading}
          className={`px-6 py-3 rounded-xl font-semibold text-white text-base shadow-md transition-all duration-200 ${
            loading
              ? "bg-blue-300 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 hover:shadow-lg"
          }`}>
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      <div className="flex flex-wrap gap-3 justify-center mb-8">
        {sampleQueries.map((kw) => (
          <button
            key={kw}
            onClick={() => setQuery(kw)}
            disabled={loading}
            className={`px-4 py-2 text-sm rounded-full border transition-all ${
              loading
                ? "bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed"
                : "bg-white text-gray-700 border-gray-200 hover:bg-blue-50 hover:text-blue-700 shadow-sm"
            }`}>
            {kw}
          </button>
        ))}
      </div>

      <div className="border-t border-gray-200 mb-6"></div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
          <p className="text-red-700 text-sm font-medium">❌ {error}</p>
        </div>
      )}

      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 mt-4">Searching...</p>
        </div>
      )}

      {!loading && (
        <div className="space-y-5">
          {results.length === 0 && !error && (
            <p className="text-gray-500 text-center italic py-12">
              No results yet — try a search above!
            </p>
          )}

          {results.map((r) => (
            <div
              key={r.id}
              className="p-6 bg-white border border-gray-100 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-200">
              <h2 className="font-semibold text-lg text-gray-900">{r.title}</h2>
              <p className="text-gray-700 mt-1 leading-relaxed">{r.body}</p>

              <div className="mt-3 flex gap-4 text-sm text-gray-500">
                {r.fts_score !== undefined && r.fts_score !== null && (
                  <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded-md">
                    FTS Score: {r.fts_score.toFixed(3)}
                  </span>
                )}
                {r.vector_score !== undefined && r.vector_score !== null && (
                  <span className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-md">
                    Vector Score: {r.vector_score.toFixed(3)}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
