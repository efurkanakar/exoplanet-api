import { ChangeEvent } from 'react';
import { PlanetFilterState } from '../hooks/usePlanetFilters';

const orderOptions = [
  { value: 'name', label: 'Name' },
  { value: 'discovery_year', label: 'Discovery Year' },
  { value: 'orbital_period', label: 'Orbital Period' },
  { value: 'radius', label: 'Radius' },
  { value: 'mass', label: 'Mass' }
];

type Props = {
  values: PlanetFilterState;
  loading?: boolean;
  onChange: (key: keyof PlanetFilterState, value: string) => void;
  onReset: () => void;
};

const PlanetFilters = ({ values, loading, onChange, onReset }: Props) => {
  const handleChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    onChange(name as keyof PlanetFilterState, value);
  };

  return (
    <form className="filters" onSubmit={(event) => event.preventDefault()}>
      <input
        name="search"
        placeholder="Search by planet name"
        value={values.search}
        onChange={handleChange}
        disabled={loading}
      />

      <input
        name="method"
        placeholder="Discovery method"
        value={values.method}
        onChange={handleChange}
        disabled={loading}
      />

      <input
        name="minYear"
        placeholder="Min year"
        value={values.minYear}
        onChange={handleChange}
        disabled={loading}
      />

      <input
        name="maxYear"
        placeholder="Max year"
        value={values.maxYear}
        onChange={handleChange}
        disabled={loading}
      />

      <select name="orderBy" value={values.orderBy} onChange={handleChange} disabled={loading}>
        {orderOptions.map((option) => (
          <option key={option.value} value={option.value}>
            Order by {option.label}
          </option>
        ))}
      </select>

      <select name="orderDir" value={values.orderDir} onChange={handleChange} disabled={loading}>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
      </select>

      <button type="button" onClick={onReset} disabled={loading}>
        Reset filters
      </button>
    </form>
  );
};

export default PlanetFilters;
