import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Paginated, Vehicle } from "../types";

export function VehiclesPage() {
  const { effectiveTenantId, user } = useAuth();
  const [rows, setRows] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role === "super_admin" && !effectiveTenantId) {
      setRows([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    api<Paginated<Vehicle>>("/vehicles/", { tenantId: effectiveTenantId })
      .then((d) => setRows(d.results))
      .finally(() => setLoading(false));
  }, [effectiveTenantId, user?.role]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Fleet vehicles</h1>
      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-800 bg-slate-900/80 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">VIN</th>
              <th className="px-4 py-3">Vehicle</th>
              <th className="px-4 py-3">Plate</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Odometer</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                  No vehicles in scope.
                </td>
              </tr>
            )}
            {rows.map((v) => (
              <tr key={v.id} className="border-b border-slate-800/60 hover:bg-slate-800/30">
                <td className="px-4 py-3 font-mono text-xs text-brand-400">{v.vin}</td>
                <td className="px-4 py-3">
                  {v.year} {v.make} {v.model}
                </td>
                <td className="px-4 py-3">{v.license_plate || "—"}</td>
                <td className="px-4 py-3 capitalize">{v.status.replace("_", " ")}</td>
                <td className="px-4 py-3">{v.odometer_km.toLocaleString()} km</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
