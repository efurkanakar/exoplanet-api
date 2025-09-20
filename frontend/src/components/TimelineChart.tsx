import { Line } from 'react-chartjs-2';
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip
} from 'chart.js';
import Skeleton from './Skeleton';
import type { DiscoveryTimelinePoint } from '../types';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

type Props = {
  series: DiscoveryTimelinePoint[];
  loading?: boolean;
};

const TimelineChart = ({ series, loading }: Props) => {
  if (loading) {
    return <Skeleton height={280} />;
  }

  const data = {
    labels: series.map((point) => point.year),
    datasets: [
      {
        label: 'Discoveries',
        data: series.map((point) => point.count),
        fill: false,
        borderColor: '#1d4ed8',
        backgroundColor: '#1d4ed8',
        tension: 0.3
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        title: {
          display: true,
          text: 'Year'
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of discoveries'
        }
      }
    }
  };

  return (
    <div style={{ height: 320 }}>
      <Line options={options} data={data} />
    </div>
  );
};

export default TimelineChart;
