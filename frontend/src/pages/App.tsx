import { NavLink, Route, Routes } from 'react-router-dom';
import DashboardPage from './DashboardPage';
import PlanetsPage from './PlanetsPage';
import VisualizationPage from './VisualizationPage';

const App = () => {
  return (
    <main>
      <header>
        <div>
          <h1>Exoplanet Explorer</h1>
          <p>Discover planets beyond our solar system using the Exoplanet API.</p>
        </div>
        <nav>
          <NavLink to="/" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`} end>
            Dashboard
          </NavLink>
          <NavLink to="/planets" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
            Catalog
          </NavLink>
          <NavLink to="/visualizations" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
            Visualizations
          </NavLink>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/planets" element={<PlanetsPage />} />
        <Route path="/visualizations" element={<VisualizationPage />} />
      </Routes>
    </main>
  );
};

export default App;
