import Skeleton from './Skeleton';
import type { PlanetListResponse } from '../types';

type Props = {
  response?: PlanetListResponse;
  loading?: boolean;
  onPageChange: (page: number) => void;
};

const PlanetsTable = ({ response, loading, onPageChange }: Props) => {
  const planets = response?.results ?? [];
  const total = response?.total ?? 0;
  const page = response?.page ?? 1;
  const pages = response?.pages ?? 1;

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Discovery Method</th>
            <th>Year</th>
            <th>Orbital Period (days)</th>
            <th>Radius (R⊕)</th>
            <th>Mass (M⊕)</th>
          </tr>
        </thead>
        <tbody>
          {loading
            ? [...Array(6)].map((_, index) => (
                <tr key={index}>
                  <td colSpan={6}>
                    <Skeleton height={20} />
                  </td>
                </tr>
              ))
            : planets.map((planet) => (
                <tr key={planet.id}>
                  <td>{planet.name}</td>
                  <td>{planet.discovery_method}</td>
                  <td>{planet.discovery_year ?? '—'}</td>
                  <td>{planet.orbital_period?.toFixed(2) ?? '—'}</td>
                  <td>{planet.radius?.toFixed(2) ?? '—'}</td>
                  <td>{planet.mass?.toFixed(2) ?? '—'}</td>
                </tr>
              ))}
        </tbody>
      </table>

      <footer className="pagination">
        <div className="badge">{total} results</div>
        <div>
          <button onClick={() => onPageChange(page - 1)} disabled={page <= 1 || loading}>
            Previous
          </button>
          <button onClick={() => onPageChange(page + 1)} disabled={page >= pages || loading}>
            Next
          </button>
        </div>
      </footer>
    </div>
  );
};

export default PlanetsTable;
