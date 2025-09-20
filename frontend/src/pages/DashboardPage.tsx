import { useDiscoveryStats, useDiscoveryTimeline } from '../hooks/useAnalytics';
import MetricCard from '../components/MetricCard';
import TimelineChart from '../components/TimelineChart';

const DashboardPage = () => {
  const { data: stats, isLoading: statsLoading, error: statsError } = useDiscoveryStats();
  const { data: timeline, isLoading: timelineLoading, error: timelineError } = useDiscoveryTimeline();

  if (statsError || timelineError) {
    return <div className="error">Unable to load dashboard metrics. Please try again later.</div>;
  }

  return (
    <section className="card-grid">
      <MetricCard
        title="Catalogued Planets"
        metric={stats?.planet_count ?? 0}
        loading={statsLoading}
        description="Total number of confirmed exoplanets in the database."
      />
      <MetricCard
        title="Median Orbital Period"
        metric={stats?.orbital_period?.median ?? 0}
        unit=" days"
        loading={statsLoading}
        description="Half of all planets orbit their star in fewer days than this value."
      />
      <MetricCard
        title="Median Planet Radius"
        metric={stats?.radius?.median ?? 0}
        unit=" R⊕"
        loading={statsLoading}
        description="The typical planet size relative to Earth."
      />
      <MetricCard
        title="Average Stellar Temperature"
        metric={stats?.stellar_temperature?.mean ?? 0}
        unit=" K"
        decimals={0}
        loading={statsLoading}
        description="Mean host-star temperature across the catalog."
      />

      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <h2>Discoveries per Year</h2>
        <p>Track how exoplanet discoveries have accelerated over time.</p>
        <TimelineChart loading={timelineLoading} series={timeline ?? []} />
      </div>
    </section>
  );
};

export default DashboardPage;
