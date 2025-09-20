import { CSSProperties } from 'react';

type Props = {
  width?: number | string;
  height?: number | string;
};

const Skeleton = ({ width = '100%', height = 16 }: Props) => {
  const style: CSSProperties = {
    width,
    height,
    borderRadius: '9999px',
    background: 'linear-gradient(90deg, rgba(148, 163, 184, 0.2) 25%, rgba(148, 163, 184, 0.35) 37%, rgba(148, 163, 184, 0.2) 63%)',
    backgroundSize: '400% 100%',
    animation: 'pulse 1.4s ease infinite'
  };

  return <div style={style} />;
};

export default Skeleton;
