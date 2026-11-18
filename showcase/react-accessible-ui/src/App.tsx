import { useId, useMemo, useState } from "react";
import { filterProjects, projects, type ProjectStatus, type StatusFilter } from "./projects";

const statuses: readonly StatusFilter[] = ["All", "Delivered", "In progress", "Planned"];

const statusClasses: Record<ProjectStatus, string> = {
  Delivered: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  "In progress": "bg-blue-50 text-blue-800 ring-blue-200",
  Planned: "bg-amber-50 text-amber-800 ring-amber-200",
};

export default function App() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<StatusFilter>("All");
  const searchId = useId();
  const filterId = useId();

  const results = useMemo(
    () => filterProjects(projects, query, status),
    [query, status]
  );

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-5xl px-5 py-12 sm:py-20">
        <header className="mb-10 max-w-2xl">
          <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">
            Atelier Williams Studio · Engineering demo
          </p>
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            Project Explorer
          </h1>
          <p className="mt-5 text-base leading-relaxed text-slate-600">
            An accessible, responsive React interface with client-side search,
            status filters and clear feedback. All projects are fictional sample data.
          </p>
        </header>

        <section aria-label="Project filters" className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="grid gap-5 sm:grid-cols-[1fr_220px]">
            <div>
              <label htmlFor={searchId} className="mb-2 block text-sm font-semibold">
                Search projects
              </label>
              <input
                id={searchId}
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search title, category or technology"
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus-visible:border-blue-600 focus-visible:ring-2 focus-visible:ring-blue-200"
              />
            </div>
            <div>
              <label htmlFor={filterId} className="mb-2 block text-sm font-semibold">
                Project status
              </label>
              <select
                id={filterId}
                value={status}
                onChange={(event) => setStatus(event.target.value as StatusFilter)}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none focus-visible:border-blue-600 focus-visible:ring-2 focus-visible:ring-blue-200"
              >
                {statuses.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <p className="mt-4 text-sm text-slate-600" role="status" aria-live="polite">
            {results.length} {results.length === 1 ? "project" : "projects"} found
          </p>
        </section>

        {results.length === 0 ? (
          <section className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center">
            <h2 className="font-semibold">No matching projects</h2>
            <p className="mt-2 text-sm text-slate-600">
              Try another search or clear your filters.
            </p>
            <button
              type="button"
              onClick={() => { setQuery(""); setStatus("All"); }}
              className="mt-5 rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
            >
              Clear filters
            </button>
          </section>
        ) : (
          <section aria-label="Matching projects" className="mt-6 grid gap-5 md:grid-cols-2">
            {results.map((project) => (
              <article
                key={project.id}
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    {project.category}
                  </span>
                  <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${statusClasses[project.status]}`}>
                    {project.status}
                  </span>
                </div>
                <h2 className="mt-5 text-xl font-bold tracking-tight">{project.title}</h2>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {project.summary}
                </p>
                <ul aria-label={`Technologies for ${project.title}`} className="mt-5 flex flex-wrap gap-2">
                  {project.tags.map((tag) => (
                    <li key={tag} className="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
                      {tag}
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </section>
        )}
        <footer className="mt-12 border-t border-slate-200 pt-5 text-sm text-slate-500">
          Standalone engineering demonstration · No API calls · No personal data
        </footer>
      </div>
    </main>
  );
}
