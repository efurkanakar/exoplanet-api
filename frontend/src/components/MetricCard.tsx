import Skeleton from './Skeleton';

type Props = {
  title: string;
  metric: number;
  unit?: string;
  decimals?: number;
  loading?: boolean;
  description?: string;
};

const formatValue = (value: number, decimals = 1) =>
  new Intl.NumberFormat('en-US', {
    maximumFractionDigits: decimals,
    minimumFractionDigits: decimals
  }).format(value);

const MetricCard = ({ title, metric, unit = '', decimals = 1, loading, description }: Props) => {
  return (
    <article className="card">
      <h2>{title}</h2>
      {loading ? (
        <Skeleton height={48} width={160} />
      ) : (
        <div className="metric">
          {formatValue(metric, decimals)}
          {unit}
        </div>
      )}
      {description && <p className="metric-label">{description}</p>}
    </article>
  );
};

export default MetricCard;
