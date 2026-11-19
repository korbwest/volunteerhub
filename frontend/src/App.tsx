import { useState } from "react";
import { Link, NavLink, Route, Routes, useNavigate } from "react-router-dom";
import { errorMessage } from "./api";
import { Feedback } from "./components";
import Auth from "./pages/Auth";
import { Catalog, OrganizationDetail, ProjectDetail } from "./pages/Catalog";
import { Editor, Manage } from "./pages/Manage";
import Profile from "./pages/Profile";
import { useSession } from "./session";

export default function App() {
  const { user, logout, loading } = useSession();
  const [error, setError] = useState("");
  const navigate = useNavigate();
  async function exit() {
    try {
      await logout();
      setError("");
      navigate("/");
    } catch (err) {
      setError(errorMessage(err));
    }
  }
  return (
    <>
      <a className="skip" href="#main">
        К содержимому
      </a>
      <header>
        <div className="nav-wrap">
          <Link className="brand" to="/">
            <span aria-hidden="true">#</span> рядом
            <span className="brand-dot">.</span>
          </Link>
          <nav aria-label="Основное меню">
            <NavLink to="/" end>
              Проекты
            </NavLink>
            <NavLink to="/organizations">Организации</NavLink>
            {user?.role === "ORGANIZER" && (
              <NavLink to="/manage">Мои проекты</NavLink>
            )}
          </nav>
          <div className="account">
            {!loading &&
              (user ? (
                <>
                  <Link to="/profile">Мой профиль</Link>
                  <button className="text-button" onClick={exit}>
                    Выйти
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login">Войти</Link>
                  <Link className="button" to="/register">
                    Присоединиться
                  </Link>
                </>
              ))}
          </div>
        </div>
      </header>
      <main id="main">
        <Feedback error={error} />
        <Routes>
          <Route path="/" element={<Catalog key="projects" />} />
          <Route
            path="/organizations"
            element={<Catalog key="organizations" organizations />}
          />
          <Route path="/organizations/:id" element={<OrganizationDetail />} />
          <Route path="/projects/:id" element={<ProjectDetail />} />
          <Route path="/login" element={<Auth key="login" />} />
          <Route path="/register" element={<Auth key="register" register />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/manage" element={<Manage />} />
          <Route path="/manage/new" element={<Editor />} />
          <Route path="/manage/:id" element={<Editor />} />
          <Route
            path="*"
            element={
              <>
                <h1>Страница не найдена</h1>
                <Link to="/">Вернуться к проектам</Link>
              </>
            }
          />
        </Routes>
      </main>
      <footer>
        <Link className="text-button" to="/">
          на главную
        </Link>
      </footer>
    </>
  );
}
