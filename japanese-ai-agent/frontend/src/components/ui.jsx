import { useEffect, useState } from "react";

export const inputCls =
  "rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-indigo-500 dark:border-slate-700 dark:bg-slate-900 dark:text-white";

export function Button({ children, className = "", ...props }) {
  return (
    <button
      {...props}
      className={`rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 ${className}`}
    >
      {children}
    </button>
  );
}

export function Notice({ children, tone = "info" }) {
  const tones = {
    info: "bg-slate-50 text-slate-600 dark:bg-slate-900 dark:text-slate-300",
    error: "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-200",
    warn: "bg-amber-50 text-amber-800 dark:bg-amber-950 dark:text-amber-200",
  };
  return <p className={`rounded-lg p-3 text-sm ${tones[tone]}`}>{children}</p>;
}

export function PageIntro({ children }) {
  return <p className="mb-4 text-sm text-slate-500">{children}</p>;
}

export const LEVELS = ["N5", "N4", "N3", "N2", "N1"];

export function LevelSelect({ value, onChange }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={inputCls}
    >
      <option value="">Semua level</option>
      {LEVELS.map((l) => (
        <option key={l} value={l}>
          {l}
        </option>
      ))}
    </select>
  );
}

export function useDebounced(value, delay = 300) {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return v;
}

// Menjalankan fungsi async setiap kali deps berubah; hasil lama dibuang bila sudah usang
export function useLoader(load, deps) {
  const [state, setState] = useState({ loading: true, error: "", data: null });
  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: "" }));
    load()
      .then(
        (data) => !cancelled && setState({ loading: false, error: "", data }),
      )
      .catch(
        (err) =>
          !cancelled &&
          setState({ loading: false, error: err.message, data: null }),
      );
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return state;
}

export function Result({ state, empty = "Tidak ada hasil.", children }) {
  if (state.loading)
    return <p className="text-sm italic text-slate-400">Memuat...</p>;
  if (state.error) return <Notice tone="error">{state.error}</Notice>;
  if (!state.data || state.data.items?.length === 0)
    return <Notice>{empty}</Notice>;
  return children;
}
