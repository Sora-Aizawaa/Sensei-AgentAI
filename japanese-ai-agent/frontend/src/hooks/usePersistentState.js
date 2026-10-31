import { useEffect, useState } from "react";

// Seperti useState, tapi nilainya disimpan di localStorage (bertahan setelah halaman dimuat ulang)
export default function usePersistentState(key, initial) {
  const [value, setValue] = useState(() => {
    try {
      const raw = localStorage.getItem(key);
      return raw === null ? initial : JSON.parse(raw);
    } catch {
      return initial;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* penyimpanan penuh atau dimatikan: abaikan */
    }
  }, [key, value]);

  return [value, setValue];
}
