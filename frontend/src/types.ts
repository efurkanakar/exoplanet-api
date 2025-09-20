export type PlanetSummary = {
  id: number;
  name: string;
  discovery_method: string;
  discovery_year: number | null;
  orbital_period: number | null;
  radius: number | null;
  mass: number | null;
};

export type PlanetListResponse = {
  results: PlanetSummary[];
  page: number;
  pages: number;
  total: number;
};

export type MetricSummary = {
  min: number | null;
  max: number | null;
  mean: number | null;
  median: number | null;
};

export type DiscoveryStats = {
  planet_count: number;
  orbital_period: MetricSummary;
  radius: MetricSummary;
  mass: MetricSummary;
  stellar_temperature: MetricSummary;
};

export type DiscoveryTimelinePoint = {
  year: number;
  count: number;
};

export type HistogramSeries = {
  bins: number[];
  counts: number[];
};

export type DiscoveryDataset = {
  histogram: HistogramSeries;
  year_series: DiscoveryTimelinePoint[];
  method_series: { method: string; count: number }[];
};
