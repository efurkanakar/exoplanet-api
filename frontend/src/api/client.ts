const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const buildUrl = (path: string, params?: Record<string, string | number | undefined>) => {
  const url = new URL(path, API_BASE_URL);
  if (params) {
    Object.entries(params)
      .filter(([, value]) => value !== undefined && value !== '')
      .forEach(([key, value]) => url.searchParams.set(key, String(value)));
  }
  return url.toString();
};

export const get = async <T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> => {
  const response = await fetch(buildUrl(path, params));
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
};
