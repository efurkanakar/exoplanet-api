import PlanetFilters from '../components/PlanetFilters';
import PlanetsTable from '../components/PlanetsTable';
import { usePlanetFilters } from '../hooks/usePlanetFilters';
import { usePlanetList } from '../hooks/usePlanetList';

const PlanetsPage = () => {
  const { filters, updateFilter, resetFilters } = usePlanetFilters();
  const { data, isLoading, error, setPage } = usePlanetList(filters);

  return (
    <section>
      <PlanetFilters
        values={filters}
        onChange={updateFilter}
        onReset={resetFilters}
        loading={isLoading}
      />

      {error && <div className="error">Failed to load planets. Please adjust your filters.</div>}

      <PlanetsTable
        response={data}
        loading={isLoading}
        onPageChange={setPage}
      />
    </section>
  );
};

export default PlanetsPage;
