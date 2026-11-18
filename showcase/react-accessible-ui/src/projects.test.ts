import { describe, expect, it } from "vitest";
import { filterProjects, projects } from "./projects";

describe("filterProjects", () => {
  it("filters case-insensitively by title or tag", () => {
    expect(filterProjects(projects, "REACT", "All").map((p) => p.id)).toEqual(["p1", "p4"]);
  });

  it("combines status and query", () => {
    expect(filterProjects(projects, "forms", "Delivered").map((p) => p.id)).toEqual(["p4"]);
  });

  it("returns an empty list for unmatched queries", () => {
    expect(filterProjects(projects, "not a real project", "All")).toEqual([]);
  });

  it("does not mutate its input", () => {
    const original = [...projects];
    filterProjects(projects, "", "All");
    expect(projects).toEqual(original);
  });
});
