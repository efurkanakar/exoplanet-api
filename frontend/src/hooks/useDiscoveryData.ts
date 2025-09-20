import { useQuery } from '@tanstack/react-query';
import { get } from '../api/client';
import type { DiscoveryDataset } from '../types';

export const useDiscoveryData = () =>
  useQuery({
    queryKey: ['discovery', 'dataset'],
    queryFn: () => get<DiscoveryDataset>('/vis/discovery', { chart: 'hist' })
  });
