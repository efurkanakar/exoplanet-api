import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { get } from '../api/client';
import type { PlanetListResponse } from '../types';
import type { PlanetFilterState } from './usePlanetFilters';

const PAGE_SIZE = 20;

type Params = PlanetFilterState;

const mapFiltersToParams = (filters: Params, page: number) => ({
  limit: PAGE_SIZE,
  page,
  name: filters.search,
  method: filters.method,
  min_year: filters.minYear,
  max_year: filters.maxYear,
  order_by: filters.orderBy,
  order_dir: filters.orderDir
});

export const usePlanetList = (filters: Params) => {
  const [page, setPage] = useState(1);

  useEffect(() => {
    setPage(1);
  }, [filters]);

  const query = useQuery({
    queryKey: ['planets', { filters, page }],
    queryFn: () => get<PlanetListResponse>('/planets', mapFiltersToParams(filters, page)),
    keepPreviousData: true
  });

  return {
    ...query,
    setPage
  };
};
