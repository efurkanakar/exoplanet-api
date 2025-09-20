import { useQuery } from '@tanstack/react-query';
import { get } from '../api/client';
import type { DiscoveryStats, DiscoveryTimelinePoint } from '../types';

export const useDiscoveryStats = () =>
  useQuery({
    queryKey: ['analytics', 'stats'],
    queryFn: () => get<DiscoveryStats>('/planets/stats')
  });

export const useDiscoveryTimeline = () =>
  useQuery({
    queryKey: ['analytics', 'timeline'],
    queryFn: () => get<DiscoveryTimelinePoint[]>('/planets/timeline')
  });
