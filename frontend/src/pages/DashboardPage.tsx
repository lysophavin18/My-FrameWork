import React, { useEffect, useState } from "react";
import { Box, Grid, Paper, Typography } from "@mui/material";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { api } from "../api/client";

const COLORS: Record<string, string> = {
  critical: "#b91c1c",
  high: "#dc2626",
  medium: "#f59e0b",
  low: "#2563eb",
  info: "#64748b",
};

export default function DashboardPage() {
  const [stats, setStats] = useState<any | null>(null);

  useEffect(() => {
    (async () => {
      const resp = await api.get("/dashboard/stats");
      setStats(resp.data);
    })();
  }, []);

  const sevData = Object.entries(stats?.severity_counts || {}).map(([k, v]) => ({
    name: k,
    value: v as number,
  }));

  return (
    <Box sx={{ color: "#e2e8f0" }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Dashboard
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, bgcolor: "#0f172a" }}>
            <Typography variant="caption" sx={{ color: "#94a3b8" }}>
              Total scans
            </Typography>
            <Typography variant="h4">{stats?.total_scans ?? "—"}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, bgcolor: "#0f172a" }}>
            <Typography variant="caption" sx={{ color: "#94a3b8" }}>
              Active scans
            </Typography>
            <Typography variant="h4">{stats?.active_scans ?? "—"}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, bgcolor: "#0f172a" }}>
            <Typography variant="caption" sx={{ color: "#94a3b8" }}>
              Findings
            </Typography>
            <Typography variant="h4">{stats?.total_findings ?? "—"}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, bgcolor: "#0f172a" }}>
            <Typography variant="caption" sx={{ color: "#94a3b8" }}>
              Unique CVEs
            </Typography>
            <Typography variant="h4">{stats?.unique_cves ?? "—"}</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, bgcolor: "#0f172a", height: 320 }}>
            <Typography variant="subtitle2" sx={{ color: "#cbd5e1", mb: 1 }}>
              Severity distribution
            </Typography>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sevData} dataKey="value" nameKey="name" outerRadius={110}>
                  {sevData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name] || "#334155"} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, bgcolor: "#0f172a", height: 320 }}>
            <Typography variant="subtitle2" sx={{ color: "#cbd5e1", mb: 1 }}>
              Recent scans
            </Typography>
            <Box sx={{ maxHeight: 260, overflow: "auto" }}>
              {(stats?.recent_scans || []).map((s: any) => (
                <Box key={s.id} sx={{ py: 1, borderBottom: "1px solid #1f2a44" }}>
                  <Typography variant="body2">
                    #{s.id} {s.target} — {s.status}
                  </Typography>
                  <Typography variant="caption" sx={{ color: "#94a3b8" }}>
                    {String(s.created_at)}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

