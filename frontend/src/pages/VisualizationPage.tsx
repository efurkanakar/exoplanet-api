import DiscoveryCharts from '../components/DiscoveryCharts';
import { useDiscoveryData } from '../hooks/useDiscoveryData';

const VisualizationPage = () => {
  const { data, isLoading, error } = useDiscoveryData();

  if (error) {
    return <div className="error">Unable to load visualization data. Please retry.</div>;
  }

  return (
    <section className="card">
      <h2>Discovery Visualizations</h2>
      <p>Explore exoplanet discoveries by stellar temperature, detection method and year.</p>
      <DiscoveryCharts loading={isLoading} discovery={data} />
    </section>
  );
};

export default VisualizationPage;
