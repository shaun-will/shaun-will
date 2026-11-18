export type ProjectStatus = "In progress" | "Delivered" | "Planned";

export type Project = {
  id: string;
  title: string;
  category: string;
  summary: string;
  status: ProjectStatus;
  tags: readonly string[];
};

export const projects: readonly Project[] = [
  {
    id: "p1",
    title: "Community archive",
    category: "Content platform",
    summary: "A searchable collection with community-led editorial review.",
    status: "Delivered",
    tags: ["React", "Accessibility", "Search"],
  },
  {
    id: "p2",
    title: "Volunteer scheduler",
    category: "Operations",
    summary: "A planning interface that reduces scheduling friction.",
    status: "In progress",
    tags: ["TypeScript", "Forms", "UX"],
  },
  {
    id: "p3",
    title: "Resource directory",
    category: "Public information",
    summary: "A multilingual directory with clear navigation and filters.",
    status: "Planned",
    tags: ["i18n", "Tailwind", "Responsive"],
  },
  {
    id: "p4",
    title: "Event registrations",
    category: "Events",
    summary: "A mobile-friendly registration flow with transparent status.",
    status: "Delivered",
    tags: ["React", "Validation", "Forms"],
  },
];

export type StatusFilter = "All" | ProjectStatus;

export function filterProjects(
  items: readonly Project[],
  query: string,
  status: StatusFilter
): Project[] {
  const needle = query.trim().toLocaleLowerCase();
  return items
    .filter((project) => status === "All" || project.status === status)
    .filter((project) => {
      if (!needle) return true;
      return [
        project.title,
        project.category,
        project.summary,
        ...project.tags,
      ]
        .join(" ")
        .toLocaleLowerCase()
        .includes(needle);
    })
    .sort((a, b) => a.title.localeCompare(b.title));
}
