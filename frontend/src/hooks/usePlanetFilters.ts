import { useState } from 'react';

export type PlanetFilterState = {
  search: string;
  method: string;
  minYear: string;
  maxYear: string;
  orderBy: string;
  orderDir: 'asc' | 'desc';
};

const defaultState: PlanetFilterState = {
  search: '',
  method: '',
  minYear: '',
  maxYear: '',
  orderBy: 'discovery_year',
  orderDir: 'desc'
};

export const usePlanetFilters = () => {
  const [filters, setFilters] = useState<PlanetFilterState>(defaultState);

  const updateFilter = (key: keyof PlanetFilterState, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => setFilters(defaultState);

  return {
    filters,
    updateFilter,
    resetFilters
  };
};
