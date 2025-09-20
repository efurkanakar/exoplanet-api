import { Bar, Doughnut } from 'react-chartjs-2';
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip
} from 'chart.js';
import Skeleton from './Skeleton';
import type { DiscoveryDataset } from '../types';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

type Props = {
  discovery?: DiscoveryDataset;
  loading?: boolean;
};

const DiscoveryCharts = ({ discovery, loading }: Props) => {
  if (loading) {
    return <Skeleton height={400} />;
  }

  if (!discovery) {
    return null;
  }

  const histogramData = {
    labels: discovery.histogram.bins,
    datasets: [
      {
        label: 'Planets per temperature bucket',
        data: discovery.histogram.counts,
        backgroundColor: '#9333ea'
      }
    ]
  };

  const methodData = {
    labels: discovery.method_series.map((item) => item.method),
    datasets: [
      {
        label: 'Discoveries',
        data: discovery.method_series.map((item) => item.count),
        backgroundColor: ['#1d4ed8', '#9333ea', '#14b8a6', '#f97316', '#6366f1', '#facc15']
      }
    ]
  };

  const yearData = {
    labels: discovery.year_series.map((item) => item.year),
    datasets: [
      {
        label: 'Discoveries',
        data: discovery.year_series.map((item) => item.count),
        backgroundColor: '#0ea5e9'
      }
    ]
  };

  return (
    <div className="card-grid">
      <div className="card">
        <h3>Stellar Temperature Histogram</h3>
        <Bar data={histogramData} options={{ maintainAspectRatio: false }} />
      </div>
      <div className="card">
        <h3>Discoveries by Method</h3>
        <Doughnut data={methodData} />
      </div>
      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <h3>Discoveries by Year</h3>
        <Bar data={yearData} options={{ maintainAspectRatio: false }} />
      </div>
    </div>
  );
};

export default DiscoveryCharts;
