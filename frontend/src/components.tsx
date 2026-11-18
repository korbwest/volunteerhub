import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, errorMessage } from "./api";
import { categories, units, type Project } from "./types";

export function useResource<T>(path: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    setData(null);
    api<T>(path)
      .then((value) => {
        if (active) setData(value);
      })
      .catch((err) => {
        if (active) setError(errorMessage(err));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [path, revision]);
  return {
    data,
    error,
    loading,
    reload: () => setRevision((value) => value + 1),
  };
}
export function Feedback({
  error,
  loading,
}: {
  error?: string;
  loading?: boolean;
}) {
  if (error)
    return (
      <p role="alert" className="error">
        {error}
      </p>
    );
  return loading ? (
    <p role="status" className="muted">
      Загружаем данные…
    </p>
  ) : null;
}
export function Empty({ title, text }: { title: string; text: string }) {
  return (
    <div className="empty">
      <span aria-hidden="true">✳</span>
      <h2>{title}</h2>
      <p>{text}</p>
    </div>
  );
}
export function Pager({
  page,
  total,
  size = 12,
  onChange,
}: {
  page: number;
  total: number;
  size?: number;
  onChange: (page: number) => void;
}) {
  if (total <= size) return null;
  return (
    <nav className="pager" aria-label="Страницы">
      <button
        className="secondary"
        disabled={page === 1}
        onClick={() => onChange(page - 1)}
      >
        Назад
      </button>
      <span>
        {page} / {Math.ceil(total / size)}
      </span>
      <button
        className="secondary"
        disabled={page * size >= total}
        onClick={() => onChange(page + 1)}
      >
        Далее
      </button>
    </nav>
  );
}
export function ProjectCard({ project }: { project: Project }) {
  return (
    <article className="project-card">
      <Link to={`/projects/${project.id}`} tabIndex={-1} aria-hidden="true">
        <img
          src={project.cover_url}
          alt=""
          loading="lazy"
          referrerPolicy="no-referrer"
        />
      </Link>
      <div className="card-body">
        <span className="tag">{categories[project.category]}</span>
        <h2>
          <Link to={`/projects/${project.id}`}>{project.title}</Link>
        </h2>
        <p className="muted">
          {project.city} ·{" "}
          {new Date(project.starts_at).toLocaleDateString("ru-RU")}
        </p>
        <p className="excerpt">{project.description}</p>
        <div className="card-bottom">
          <span>
            {project.duration} {units[project.duration_unit]}
          </span>
          <Link to={`/projects/${project.id}`}>Подробнее →</Link>
        </div>
      </div>
    </article>
  );
}
