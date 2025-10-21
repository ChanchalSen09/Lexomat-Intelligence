"use client";

import { useState } from "react";
import axios from "axios";
import { FiSearch } from "react-icons/fi"; // search icon

export default function SearchBox() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("hybrid");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return; // prevent empty search
    setLoading(true);

    try {
      const res = await axios.post(
        "http://localhost:8000/search",
        { query, mode },
        { timeout: 5000 }
      );
      setResults(res.data);
    } catch (err) {
      console.error(err);
      alert("Search failed. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto mt-16 p-6 bg-white shadow-md rounded-lg">
      <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
        Hybrid Search Demo
      </h1>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="flex flex-1 items-center border border-gray-300 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-blue-400">
          <FiSearch className="ml-2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Enter your query..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 p-2 outline-none text-gray-700"
          />
        </div>

        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className="p-2 border border-gray-300 rounded-lg bg-white text-gray-700">
          <option value="keyword">Keyword</option>
          <option value="semantic">Semantic</option>
          <option value="hybrid">Hybrid</option>
        </select>

        <button
          onClick={handleSearch}
          className={`p-2 rounded-lg text-white font-semibold ${
            loading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
          disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      <div className="space-y-4">
        {results.length === 0 && !loading && (
          <p className="text-gray-500 text-center">
            No results yet. Try searching something!
          </p>
        )}

        {results.map((r) => (
          <div
            key={r.id}
            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow duration-200">
            <h2 className="font-semibold text-lg text-gray-800">{r.title}</h2>
            <p className="text-gray-600 mt-1">{r.body}</p>

            <div className="mt-2 flex gap-4 text-sm text-gray-500">
              {r.fts_score !== undefined && (
                <span>FTS Score: {r.fts_score.toFixed(3)}</span>
              )}
              {r.vector_score !== undefined && (
                <span>Vector Score: {r.vector_score.toFixed(3)}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
