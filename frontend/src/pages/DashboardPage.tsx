import React, { useEffect, useState } from "react";
import { Box, Grid, Paper, Typography } from "@mui/material";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { api } from "../api/client";

const COLORS: Record<string, string> = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#f59e0b",
  low: "#3b82f6",
  info: "#06b6d4",
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
    name: String(k).charAt(0).toUpperCase() + String(k).slice(1),
    value: v as number,
  }));

  return (
    <Box sx={{ color: "#e8eaf6" }}>
      <Box className="section-header">
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0 }}>
          Dashboard
        </Typography>
        <Typography variant="body2" sx={{ color: "#b0bec5", mt: 1 }}>
          Real-time vulnerability assessment and penetration testing metrics
        </Typography>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper 
            sx={{ 
              p: 2.5, 
              bgcolor: "#1a2847", 
              borderLeft: "4px solid #3b82f6",
              borderRadius: 2,
              transition: "all 0.2s ease",
              "&:hover": { bgcolor: "#1f3454", transform: "translateY(-2px)" }
            }}
          >
            <Typography variant="caption" sx={{ color: "#7a8fa3", fontWeight: 600 }}>
              TOTAL SCANS
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, mt: 0.5 }}>
              {stats?.total_scans ?? "—"}
            </Typography>
            <Typography variant="caption" sx={{ color: "#7a8fa3" }}>
              All scan types combined
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper 
            sx={{ 
              p: 2.5, 
              bgcolor: "#1a2847",
              borderLeft: "4px solid #f59e0b",
              borderRadius: 2,
              transition: "all 0.2s ease",
              "&:hover": { bgcolor: "#1f3454", transform: "translateY(-2px)" }
            }}
          >
            <Typography variant="caption" sx={{ color: "#7a8fa3", fontWeight: 600 }}>
              ACTIVE SCANS
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, mt: 0.5 }}>
              {stats?.active_scans ?? "—"}
            </Typography>
            <Typography variant="caption" sx={{ color: "#7a8fa3" }}>
              Running or queued
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper 
            sx={{ 
              p: 2.5, 
              bgcolor: "#1a2847",
              borderLeft: "4px solid #ef4444",
              borderRadius: 2,
              transition: "all 0.2s ease",
              "&:hover": { bgcolor: "#1f3454", transform: "translateY(-2px)" }
            }}
          >
            <Typography variant="caption" sx={{ color: "#7a8fa3", fontWeight: 600 }}>
              FINDINGS
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, mt: 0.5 }}>
              {stats?.total_findings ?? "—"}
            </Typography>
            <Typography variant="caption" sx={{ color: "#7a8fa3" }}>
              Vulnerabilities discovered
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper 
            sx={{ 
              p: 2.5, 
              bgcolor: "#1a2847",
              borderLeft: "4px solid #10b981",
              borderRadius: 2,
              transition: "all 0.2s ease",
              "&:hover": { bgcolor: "#1f3454", transform: "translateY(-2px)" }
            }}
          >
            <Typography variant="caption" sx={{ color: "#7a8fa3", fontWeight: 600 }}>
              CVE FINDINGS
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, mt: 0.5 }}>
              {stats?.unique_cves ?? "—"}
            </Typography>
            <Typography variant="caption" sx={{ color: "#7a8fa3" }}>
              Tracked CVEs
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, bgcolor: "#1a2847", height: 360, borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: "#cbd5e1", mb: 2, fontWeight: 700 }}>
              Severity Distribution
            </Typography>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sevData} dataKey="value" nameKey="name" outerRadius={110}>
                  {sevData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name.toLowerCase()] || "#334155"} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: "#0a0e27", border: "1px solid #60a5fa", borderRadius: 8 }}
                  labelStyle={{ color: "#e8eaf6" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, bgcolor: "#1a2847", height: 360, borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: "#cbd5e1", mb: 2, fontWeight: 700 }}>
              Recent Scans
            </Typography>
            <Box sx={{ maxHeight: 300, overflow: "auto" }}>
              {(stats?.recent_scans || []).map((s: any, idx: number) => (
                <Box 
                  key={idx} 
                  sx={{ 
                    py: 1.5, 
                    px: 1,
                    borderBottom: "1px solid #1f3454",
                    "&:hover": { bgcolor: "rgba(59, 130, 246, 0.05)" }
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    #{s.id} {s.target}
                  </Typography>
                  <Typography variant="caption" sx={{ color: "#7a8fa3" }}>
                    {s.status.toUpperCase()} • {String(s.created_at).split("T")[0]}
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

