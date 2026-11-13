import { useState } from "react";

const EXPRESS_API_URL = "http://localhost:3001";

function App() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
    setReport(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (files.length === 0) {
      setError("Please select at least one document.");
      return;
    }

    setLoading(true);
    setError(null);
    setReport(null);

    const formData = new FormData();
    files.forEach((file) => formData.append("documents", file));

    try {
      const response = await fetch(`${EXPRESS_API_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data = await response.json();
      setReport(data);
    } catch (err) {
      setError(`Failed to analyze documents: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white px-4 py-10">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">
          AI Agent for Contradiction Detection
        </h1>
        <p className="text-slate-400 mb-8">
          Upload two or more company policy documents to detect contradictory rules.
        </p>

        <div className="bg-slate-800 rounded-xl p-6 mb-8 border border-slate-700">
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Select documents (PDF, DOCX, TXT)
          </label>
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            className="block w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4
                       file:rounded-lg file:border-0 file:bg-indigo-600 file:text-white
                       file:cursor-pointer hover:file:bg-indigo-500 cursor-pointer"
          />

          {files.length > 0 && (
            <ul className="mt-3 text-sm text-slate-400 list-disc list-inside">
              {files.map((f, i) => (
                <li key={i}>{f.name}</li>
              ))}
            </ul>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="mt-5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-600
                       disabled:cursor-not-allowed text-white font-medium py-2 px-6
                       rounded-lg transition-colors"
          >
            {loading ? "Analyzing..." : "Analyze Documents"}
          </button>
        </div>

        {error && (
          <div className="bg-red-900/40 border border-red-700 text-red-200 rounded-lg p-4 mb-8">
            {error}
          </div>
        )}

        {report && (
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Contradiction Report</h2>
              <span className="text-sm text-slate-400">
                {report.total_claims} claims analyzed · {report.total_contradictions} contradiction(s) found
              </span>
            </div>

            {report.total_contradictions === 0 ? (
              <p className="text-green-400">No contradictions found. ✅</p>
            ) : (
              <div className="space-y-4">
                {report.contradictions.map((c) => (
                  <div
                    key={c.id}
                    className="bg-slate-900 border border-slate-700 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-indigo-400 font-medium capitalize">
                        {c.topic || "Unknown topic"}
                      </span>
                      <span className="text-xs text-slate-500">
                        confidence: {c.confidence} · method: {c.detection_method}
                      </span>
                    </div>

                    <div className="grid md:grid-cols-2 gap-3 mb-3">
                      <div className="bg-slate-800 rounded-lg p-3">
                        <p className="text-xs text-slate-500 mb-1">
                          {c.statement_1.source}
                        </p>
                        <p className="text-sm">{c.statement_1.text}</p>
                      </div>
                      <div className="bg-slate-800 rounded-lg p-3">
                        <p className="text-xs text-slate-500 mb-1">
                          {c.statement_2.source}
                        </p>
                        <p className="text-sm">{c.statement_2.text}</p>
                      </div>
                    </div>

                    <p className="text-sm text-slate-400">
                      <span className="font-medium text-slate-300">Why: </span>
                      {c.explanation}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;