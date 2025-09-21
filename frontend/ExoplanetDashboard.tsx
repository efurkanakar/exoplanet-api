import React, { useCallback, useEffect, useMemo, useState } from "react";

type Planet = {
  id: number;
  name: string;
  disc_method: string;
  disc_year: number;
  orbperd: number;
  rade: number;
  masse: number;
  st_teff: number;
  st_rad: number;
  st_mass: number;
};

type PlanetListResponse = {
  items: Planet[];
  limit: number;
  offset: number;
  total: number;
};

type MethodCount = {
  disc_method: string;
  count: number;
};

type MetricSummary = {
  min: number | null;
  max: number | null;
  avg: number | null;
};

type PlanetStats = {
  count: number;
  orbperd: MetricSummary;
  rade: MetricSummary;
  masse: MetricSummary;
  st_teff: MetricSummary;
  st_rad: MetricSummary;
  st_mass: MetricSummary;
};

type Filters = {
  name: string;
  disc_method: string;
  min_year: string;
  max_year: string;
  min_orbperd: string;
  max_orbperd: string;
  min_rade: string;
  max_rade: string;
  min_masse: string;
  max_masse: string;
  min_st_teff: string;
  max_st_teff: string;
  min_st_rad: string;
  max_st_rad: string;
  min_st_mass: string;
  max_st_mass: string;
  include_deleted: boolean;
  sort_by: "id" | "name" | "disc_year" | "disc_method" | "orbperd" | "rade" | "masse" | "st_teff" | "st_rad" | "st_mass" | "created_at";
  sort_order: "asc" | "desc";
};

type FetchState = {
  planets: PlanetListResponse | null;
  methodCounts: MethodCount[];
  stats: PlanetStats | null;
  loading: boolean;
  error: string | null;
};

const DEFAULT_FILTERS: Filters = {
  name: "",
  disc_method: "",
  min_year: "",
  max_year: "",
  min_orbperd: "",
  max_orbperd: "",
  min_rade: "",
  max_rade: "",
  min_masse: "",
  max_masse: "",
  min_st_teff: "",
  max_st_teff: "",
  min_st_rad: "",
  max_st_rad: "",
  min_st_mass: "",
  max_st_mass: "",
  include_deleted: false,
  sort_by: "id",
  sort_order: "desc",
};

const DEFAULT_BASE_URL = "https://exoplanet-api-lg16.onrender.com";

const numericOrUndefined = (value: string): number | undefined => {
  if (value.trim() === "") {
    return undefined;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
};

const formatNumber = (value: number | null | undefined, fractionDigits = 2) => {
  if (value === null || value === undefined) {
    return "-";
  }
  return value.toLocaleString(undefined, {
    maximumFractionDigits: fractionDigits,
  });
};

const usePersistentBaseUrl = (): [string, (value: string) => void] => {
  const storageKey = "exoplanet-api-base-url";
  const [baseUrl, setBaseUrl] = useState(() => {
    if (typeof window === "undefined") {
      return DEFAULT_BASE_URL;
    }
    const stored = window.localStorage.getItem(storageKey);
    return stored?.trim() || DEFAULT_BASE_URL;
  });

  const update = (value: string) => {
    setBaseUrl(value);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(storageKey, value);
    }
  };

  return [baseUrl, update];
};

const QueryPreview: React.FC<{ baseUrl: string; params: URLSearchParams }> = ({
  baseUrl,
  params,
}) => {
  const query = params.toString();
  const url = query ? `${baseUrl}/planets?${query}` : `${baseUrl}/planets`;
  return (
    <code style={{ wordBreak: "break-all", display: "block" }}>{url}</code>
  );
};

const StatsCard: React.FC<{
  title: string;
  summary?: MetricSummary | null;
}> = ({ title, summary }) => (
  <div
    style={{
      border: "1px solid #e2e8f0",
      borderRadius: "0.5rem",
      padding: "0.75rem",
      background: "#f8fafc",
      flex: "1 1 200px",
    }}
  >
    <h4 style={{ margin: "0 0 0.5rem", fontSize: "0.9rem", color: "#0f172a" }}>
      {title}
    </h4>
    {summary ? (
      <dl style={{ margin: 0, fontSize: "0.85rem", color: "#334155" }}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <dt>Min</dt>
          <dd>{formatNumber(summary.min)}</dd>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <dt>Avg</dt>
          <dd>{formatNumber(summary.avg)}</dd>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <dt>Max</dt>
          <dd>{formatNumber(summary.max)}</dd>
        </div>
      </dl>
    ) : (
      <p style={{ margin: 0, color: "#475569" }}>Veri bulunamadı.</p>
    )}
  </div>
);

const ExoplanetDashboard: React.FC = () => {
  const [baseUrl, setBaseUrl] = usePersistentBaseUrl();
  const [filters, setFilters] = useState<Filters>(() => ({ ...DEFAULT_FILTERS }));
  const [appliedFilters, setAppliedFilters] = useState<Filters>(() => ({ ...DEFAULT_FILTERS }));
  const [limit, setLimit] = useState(25);
  const [offset, setOffset] = useState(0);
  const [{ planets, methodCounts, stats, loading, error }, setFetchState] =
    useState<FetchState>({
      planets: null,
      methodCounts: [],
      stats: null,
      loading: false,
      error: null,
    });

  const buildParams = useCallback((source: Filters, useOffset: number) => {
    const params = new URLSearchParams();
    params.set("limit", String(limit));
    params.set("offset", String(useOffset));
    if (source.name.trim()) params.set("name", source.name.trim());
    if (source.disc_method.trim())
      params.set("disc_method", source.disc_method.trim());
    if (source.include_deleted) params.set("include_deleted", "true");
    params.set("sort_by", source.sort_by);
    params.set("sort_order", source.sort_order);

    const numericFilters: Array<[keyof Filters, string]> = [
      ["min_year", "min_year"],
      ["max_year", "max_year"],
      ["min_orbperd", "min_orbperd"],
      ["max_orbperd", "max_orbperd"],
      ["min_rade", "min_rade"],
      ["max_rade", "max_rade"],
      ["min_masse", "min_masse"],
      ["max_masse", "max_masse"],
      ["min_st_teff", "min_st_teff"],
      ["max_st_teff", "max_st_teff"],
      ["min_st_rad", "min_st_rad"],
      ["max_st_rad", "max_st_rad"],
      ["min_st_mass", "min_st_mass"],
      ["max_st_mass", "max_st_mass"],
    ];

    numericFilters.forEach(([key, param]) => {
      const value = numericOrUndefined(source[key]);
      if (value !== undefined) {
        params.set(param, String(value));
      }
    });

    return params;
  }, [limit]);

  const queryParams = useMemo(
    () => buildParams(appliedFilters, offset),
    [appliedFilters, buildParams, offset]
  );

  const previewParams = useMemo(
    () => buildParams(filters, 0),
    [buildParams, filters]
  );

  const fetchAll = async (signal?: AbortSignal) => {
    setFetchState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const planetsPromise = fetch(`${baseUrl}/planets?${queryParams.toString()}`, {
        signal,
      }).then(async (res) => {
        if (!res.ok) {
          throw new Error(`Gezegenler getirilemedi: ${res.status}`);
        }
        return (await res.json()) as PlanetListResponse;
      });

      const methodCountsPromise = fetch(`${baseUrl}/planets/method-counts`, {
        signal,
      }).then(async (res) => {
        if (!res.ok) {
          throw new Error(`Yöntem istatistikleri getirilemedi: ${res.status}`);
        }
        return (await res.json()) as MethodCount[];
      });

      const statsPromise = fetch(`${baseUrl}/planets/stats`, {
        signal,
      }).then(async (res) => {
        if (!res.ok) {
          throw new Error(`İstatistikler getirilemedi: ${res.status}`);
        }
        return (await res.json()) as PlanetStats;
      });

      const [planetsResponse, methodCountsResponse, statsResponse] =
        await Promise.all([planetsPromise, methodCountsPromise, statsPromise]);

      setFetchState({
        planets: planetsResponse,
        methodCounts: methodCountsResponse,
        stats: statsResponse,
        loading: false,
        error: null,
      });
    } catch (err) {
      if ((err as Error).name === "AbortError") {
        return;
      }
      setFetchState({
        planets: null,
        methodCounts: [],
        stats: null,
        loading: false,
        error: (err as Error).message,
      });
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    fetchAll(controller.signal);
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baseUrl, queryParams.toString()]);

  const totalPages = useMemo(() => {
    if (!planets) return 0;
    return Math.ceil(planets.total / limit);
  }, [planets, limit]);

  const currentPage = useMemo(() => {
    return Math.floor(offset / limit) + 1;
  }, [offset, limit]);

  const handleFilterChange = <K extends keyof Filters>(key: K, value: Filters[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setAppliedFilters({ ...filters });
    setOffset(0);
  };

  const goToPage = (page: number) => {
    const safePage = Math.max(1, page);
    const newOffset = (safePage - 1) * limit;
    setOffset(newOffset);
  };

  const canGoPrev = offset > 0;
  const canGoNext = planets ? offset + limit < planets.total : false;

  return (
    <div
      style={{
        fontFamily: "'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        padding: "1.5rem",
        maxWidth: "1200px",
        margin: "0 auto",
        color: "#0f172a",
      }}
    >
      <header style={{ marginBottom: "1.5rem" }}>
        <h1 style={{ margin: "0 0 0.5rem", fontSize: "2rem" }}>Exoplanet Explorer</h1>
        <p style={{ margin: 0, color: "#475569" }}>
          Exoplanet API verilerini keşfetmek için filtreleyin, sıralayın ve istatistikleri inceleyin.
        </p>
      </header>

      <section
        style={{
          border: "1px solid #e2e8f0",
          borderRadius: "0.75rem",
          padding: "1rem",
          marginBottom: "1.5rem",
          background: "white",
          boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
        }}
      >
        <form onSubmit={handleSubmit}>
          <div style={{ display: "grid", gap: "1rem" }}>
            <div style={{ display: "grid", gap: "0.5rem" }}>
              <label style={{ fontWeight: 600 }}>
                API Temel Adresi
                <input
                  type="url"
                  value={baseUrl}
                  onChange={(event) => setBaseUrl(event.target.value)}
                  placeholder={DEFAULT_BASE_URL}
                  style={{
                    width: "100%",
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5f5",
                    marginTop: "0.25rem",
                  }}
                />
              </label>
              <small style={{ color: "#64748b" }}>
                Yayındaki API için varsayılan değer olan <code>{DEFAULT_BASE_URL}</code> kullanılır.
                Yerel geliştirme yapıyorsanız <code>http://localhost:8000</code> adresine
                geçebilirsiniz.
              </small>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                gap: "0.75rem",
              }}
            >
              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Ad (içeren arama)</span>
                <input
                  type="text"
                  value={filters.name}
                  onChange={(event) => handleFilterChange("name", event.target.value)}
                  placeholder="Örn. Kepler"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Keşif Yöntemi</span>
                <input
                  type="text"
                  value={filters.disc_method}
                  onChange={(event) => handleFilterChange("disc_method", event.target.value)}
                  placeholder="Örn. Transit"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Min. Keşif Yılı</span>
                <input
                  type="number"
                  value={filters.min_year}
                  onChange={(event) => handleFilterChange("min_year", event.target.value)}
                  placeholder="1995"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Maks. Keşif Yılı</span>
                <input
                  type="number"
                  value={filters.max_year}
                  onChange={(event) => handleFilterChange("max_year", event.target.value)}
                  placeholder="2025"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Min. Orbital Periyot</span>
                <input
                  type="number"
                  value={filters.min_orbperd}
                  onChange={(event) => handleFilterChange("min_orbperd", event.target.value)}
                  placeholder="0.5"
                  step="0.1"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Maks. Orbital Periyot</span>
                <input
                  type="number"
                  value={filters.max_orbperd}
                  onChange={(event) => handleFilterChange("max_orbperd", event.target.value)}
                  placeholder="400"
                  step="0.1"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Min. Yarıçap (R⊕)</span>
                <input
                  type="number"
                  value={filters.min_rade}
                  onChange={(event) => handleFilterChange("min_rade", event.target.value)}
                  placeholder="0.5"
                  step="0.1"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Maks. Yarıçap (R⊕)</span>
                <input
                  type="number"
                  value={filters.max_rade}
                  onChange={(event) => handleFilterChange("max_rade", event.target.value)}
                  placeholder="15"
                  step="0.1"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Min. Kütle (M⊕)</span>
                <input
                  type="number"
                  value={filters.min_masse}
                  onChange={(event) => handleFilterChange("min_masse", event.target.value)}
                  placeholder="0.1"
                  step="0.1"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Maks. Kütle (M⊕)</span>
                <input
                  type="number"
                  value={filters.max_masse}
                  onChange={(event) => handleFilterChange("max_masse", event.target.value)}
                  placeholder="1000"
                  step="0.1"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Min. Yüzey Sıcaklığı (K)</span>
                <input
                  type="number"
                  value={filters.min_st_teff}
                  onChange={(event) => handleFilterChange("min_st_teff", event.target.value)}
                  placeholder="2000"
                  step="50"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Maks. Yüzey Sıcaklığı (K)</span>
                <input
                  type="number"
                  value={filters.max_st_teff}
                  onChange={(event) => handleFilterChange("max_st_teff", event.target.value)}
                  placeholder="7500"
                  step="50"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Min. Yıldız Yarıçapı (R☉)</span>
                <input
                  type="number"
                  value={filters.min_st_rad}
                  onChange={(event) => handleFilterChange("min_st_rad", event.target.value)}
                  placeholder="0.1"
                  step="0.1"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Maks. Yıldız Yarıçapı (R☉)</span>
                <input
                  type="number"
                  value={filters.max_st_rad}
                  onChange={(event) => handleFilterChange("max_st_rad", event.target.value)}
                  placeholder="10"
                  step="0.1"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Min. Yıldız Kütlesi (M☉)</span>
                <input
                  type="number"
                  value={filters.min_st_mass}
                  onChange={(event) => handleFilterChange("min_st_mass", event.target.value)}
                  placeholder="0.1"
                  step="0.1"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Maks. Yıldız Kütlesi (M☉)</span>
                <input
                  type="number"
                  value={filters.max_st_mass}
                  onChange={(event) => handleFilterChange("max_st_mass", event.target.value)}
                  placeholder="5"
                  step="0.1"
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>

              <label
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  paddingTop: "1.5rem",
                }}
              >
                <input
                  type="checkbox"
                  checked={filters.include_deleted}
                  onChange={(event) =>
                    handleFilterChange("include_deleted", event.target.checked)
                  }
                />
                <span>Silinmiş gezegenleri dahil et</span>
              </label>
            </div>

            <div
              style={{
                display: "grid",
                gap: "0.75rem",
                gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              }}
            >
              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Sırala</span>
                <select
                  value={filters.sort_by}
                  onChange={(event) =>
                    handleFilterChange("sort_by", event.target.value as Filters["sort_by"])
                  }
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                >
                  <option value="id">ID</option>
                  <option value="name">Ad</option>
                  <option value="disc_year">Keşif yılı</option>
                  <option value="disc_method">Keşif yöntemi</option>
                  <option value="orbperd">Orbital periyot</option>
                  <option value="rade">Yarıçap</option>
                  <option value="masse">Kütle</option>
                  <option value="st_teff">Yıldız sıcaklığı</option>
                  <option value="st_rad">Yıldız yarıçapı</option>
                  <option value="st_mass">Yıldız kütlesi</option>
                  <option value="created_at">Oluşturulma</option>
                </select>
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Sıralama yönü</span>
                <select
                  value={filters.sort_order}
                  onChange={(event) =>
                    handleFilterChange("sort_order", event.target.value as Filters["sort_order"])
                  }
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                >
                  <option value="asc">Artan</option>
                  <option value="desc">Azalan</option>
                </select>
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <span>Sayfa başına kayıt</span>
                <input
                  type="number"
                  min={1}
                  max={200}
                  value={limit}
                  onChange={(event) => {
                    const next = Math.min(200, Math.max(1, Number(event.target.value) || 1));
                    setLimit(next);
                    setOffset(0);
                  }}
                  style={{
                    padding: "0.5rem 0.75rem",
                    borderRadius: "0.5rem",
                    border: "1px solid #cbd5e1",
                  }}
                />
              </label>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <button
                type="submit"
                style={{
                  background: "#2563eb",
                  color: "white",
                  padding: "0.6rem 1.25rem",
                  border: "none",
                  borderRadius: "0.5rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  boxShadow: "0 1px 2px rgba(37, 99, 235, 0.4)",
                }}
                disabled={loading}
              >
                {loading ? "Yükleniyor..." : "Filtreleri Uygula"}
              </button>

              <button
                type="button"
                onClick={() => {
                  setFilters({ ...DEFAULT_FILTERS });
                  setAppliedFilters({ ...DEFAULT_FILTERS });
                  setLimit(25);
                  setOffset(0);
                }}
                style={{
                  background: "transparent",
                  color: "#2563eb",
                  padding: "0.6rem 1.25rem",
                  border: "1px solid #bfdbfe",
                  borderRadius: "0.5rem",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                Sıfırla
              </button>
            </div>
          </div>
        </form>

        <div style={{ marginTop: "1rem" }}>
          <h3 style={{ margin: "0 0 0.5rem" }}>Sorgu Önizlemesi</h3>
          <QueryPreview baseUrl={baseUrl} params={previewParams} />
        </div>
      </section>

      {error && (
        <div
          style={{
            border: "1px solid #fecaca",
            background: "#fee2e2",
            color: "#991b1b",
            padding: "0.75rem 1rem",
            borderRadius: "0.5rem",
            marginBottom: "1.5rem",
          }}
        >
          {error}
        </div>
      )}

      <section style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ marginBottom: "0.75rem" }}>İstatistikler</h2>
        {stats ? (
          <div
            style={{
              display: "grid",
              gap: "1rem",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            }}
          >
            <div
              style={{
                border: "1px solid #e2e8f0",
                borderRadius: "0.5rem",
                padding: "0.75rem",
                background: "#f1f5f9",
              }}
            >
              <h4 style={{ margin: "0 0 0.5rem" }}>Toplam Gezegen</h4>
              <p style={{ margin: 0, fontSize: "1.5rem", fontWeight: 700 }}>
                {stats.count.toLocaleString()}
              </p>
            </div>
            <StatsCard title="Orbital Periyot (gün)" summary={stats.orbperd} />
            <StatsCard title="Gezegen Yarıçapı (Dünya)" summary={stats.rade} />
            <StatsCard title="Gezegen Kütlesi (Dünya)" summary={stats.masse} />
            <StatsCard title="Yıldız Sıcaklığı (K)" summary={stats.st_teff} />
            <StatsCard title="Yıldız Yarıçapı (Güneş)" summary={stats.st_rad} />
            <StatsCard title="Yıldız Kütlesi (Güneş)" summary={stats.st_mass} />
          </div>
        ) : (
          <p style={{ color: "#475569" }}>İstatistikler yükleniyor...</p>
        )}
      </section>

      <section style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ marginBottom: "0.75rem" }}>Keşif Yöntemine Göre Dağılım</h2>
        {methodCounts.length > 0 ? (
          <div style={{ display: "grid", gap: "0.5rem" }}>
            {methodCounts.map((item) => (
              <div
                key={item.disc_method}
                style={{
                  display: "grid",
                  gridTemplateColumns: "2fr 1fr",
                  alignItems: "center",
                  gap: "0.75rem",
                  padding: "0.6rem 0.75rem",
                  border: "1px solid #e2e8f0",
                  borderRadius: "0.5rem",
                  background: "white",
                }}
              >
                <span style={{ fontWeight: 500 }}>{item.disc_method}</span>
                <span style={{ textAlign: "right", color: "#2563eb", fontWeight: 600 }}>
                  {item.count.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: "#475569" }}>Yöntem verileri yükleniyor...</p>
        )}
      </section>

      <section>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ marginBottom: "0.75rem" }}>Gezegenler</h2>
          {planets && (
            <span style={{ color: "#475569" }}>
              Toplam {planets.total.toLocaleString()} kayıt • {limit} / sayfa
            </span>
          )}
        </div>

        <div style={{ overflowX: "auto", borderRadius: "0.75rem", border: "1px solid #e2e8f0" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", minWidth: "900px" }}>
            <thead style={{ background: "#f1f5f9" }}>
              <tr>
                {[
                  "ID",
                  "Ad",
                  "Keşif yöntemi",
                  "Keşif yılı",
                  "Orbital periyot (gün)",
                  "Yarıçap (R⊕)",
                  "Kütle (M⊕)",
                  "Yıldız sıcaklığı (K)",
                  "Yıldız yarıçapı (R☉)",
                  "Yıldız kütlesi (M☉)",
                ].map((header) => (
                  <th
                    key={header}
                    style={{
                      textAlign: "left",
                      padding: "0.75rem",
                      fontSize: "0.85rem",
                      color: "#0f172a",
                      borderBottom: "1px solid #e2e8f0",
                    }}
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={10} style={{ textAlign: "center", padding: "1.5rem", color: "#475569" }}>
                    Yükleniyor...
                  </td>
                </tr>
              ) : planets && planets.items.length > 0 ? (
                planets.items.map((planet) => (
                  <tr key={planet.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
                    <td style={{ padding: "0.75rem", fontVariantNumeric: "tabular-nums" }}>{planet.id}</td>
                    <td style={{ padding: "0.75rem", fontWeight: 600 }}>{planet.name}</td>
                    <td style={{ padding: "0.75rem" }}>{planet.disc_method}</td>
                    <td style={{ padding: "0.75rem", fontVariantNumeric: "tabular-nums" }}>
                      {planet.disc_year}
                    </td>
                    <td style={{ padding: "0.75rem", fontVariantNumeric: "tabular-nums" }}>
                      {formatNumber(planet.orbperd)}
                    </td>
                    <td style={{ padding: "0.75rem", fontVariantNumeric: "tabular-nums" }}>
                      {formatNumber(planet.rade)}
                    </td>
                    <td style={{ padding: "0.75rem", fontVariantNumeric: "tabular-nums" }}>
                      {formatNumber(planet.masse)}
                    </td>
                    <td style={{ padding: "0.75rem", fontVariantNumeric: "tabular-nums" }}>
                      {formatNumber(planet.st_teff)}
                    </td>
                    <td style={{ padding: "0.75rem", fontVariantNumeric: "tabular-nums" }}>
                      {formatNumber(planet.st_rad)}
                    </td>
                    <td style={{ padding: "0.75rem", fontVariantNumeric: "tabular-nums" }}>
                      {formatNumber(planet.st_mass)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={10} style={{ textAlign: "center", padding: "1.5rem", color: "#475569" }}>
                    Filtrelere uygun gezegen bulunamadı.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginTop: "1rem",
            gap: "1rem",
            flexWrap: "wrap",
          }}
        >
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <button
              type="button"
              onClick={() => goToPage(currentPage - 1)}
              disabled={!canGoPrev}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "0.5rem",
                border: "1px solid #cbd5e1",
                background: canGoPrev ? "white" : "#e2e8f0",
                color: canGoPrev ? "#0f172a" : "#94a3b8",
                cursor: canGoPrev ? "pointer" : "not-allowed",
              }}
            >
              Önceki
            </button>
            <span style={{ color: "#475569" }}>
              Sayfa {currentPage}
              {totalPages > 0 ? ` / ${totalPages}` : ""}
            </span>
            <button
              type="button"
              onClick={() => goToPage(currentPage + 1)}
              disabled={!canGoNext}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "0.5rem",
                border: "1px solid #cbd5e1",
                background: canGoNext ? "white" : "#e2e8f0",
                color: canGoNext ? "#0f172a" : "#94a3b8",
                cursor: canGoNext ? "pointer" : "not-allowed",
              }}
            >
              Sonraki
            </button>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>Sayfaya git:</span>
            <input
              type="number"
              min={1}
              value={currentPage}
              onChange={(event) => {
                const value = Number(event.target.value);
                if (Number.isFinite(value)) {
                  goToPage(value);
                }
              }}
              style={{
                width: "80px",
                padding: "0.4rem 0.6rem",
                borderRadius: "0.5rem",
                border: "1px solid #cbd5e1",
              }}
            />
          </div>
        </div>
      </section>
    </div>
  );
};

export default ExoplanetDashboard;
