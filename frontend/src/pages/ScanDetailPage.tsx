import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Box, Button, Chip, Paper, Stack, Typography } from "@mui/material";
import { api } from "../api/client";
import { useAuth } from "../state/AuthProvider";

function statusChipColor(status: string): "default" | "success" | "warning" | "error" | "info" {
  if (["completed", "done", "success"].includes(status)) return "success";
  if (["running", "queued", "pending", "approved"].includes(status)) return "info";
  if (["pending_approval"].includes(status)) return "warning";
  if (["failed", "denied", "error"].includes(status)) return "error";
  return "default";
}

function severityChipColor(severity: string): "default" | "success" | "warning" | "error" | "info" {
  if (severity === "critical" || severity === "high") return "error";
  if (severity === "medium") return "warning";
  if (severity === "low") return "info";
  if (severity === "info") return "success";
  return "default";
}

export default function ScanDetailPage() {
  const { scanId } = useParams();
  const { user } = useAuth();
  const [scan, setScan] = useState<any | null>(null);
  const [findings, setFindings] = useState<any[]>([]);

  async function load() {
    const s = await api.get(`/scans/${scanId}`);
    setScan(s.data);
    const f = await api.get(`/scans/${scanId}/findings`);
    setFindings(f.data);
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, [scanId]);

  if (!scan) return null;

  return (
    <Box sx={{ color: "#e2e8f0" }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Scan #{scan.id} details
      </Typography>

      <Paper sx={{ p: 2.5, bgcolor: "#0f172a", mb: 2, borderRadius: 3 }}>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1.5} justifyContent="space-between" sx={{ mb: 1 }}>
          <Box>
            <Typography variant="caption" sx={{ color: "#94a3b8" }}>
              Target
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 700 }}>
              {scan.target}
            </Typography>
            <Typography variant="caption" sx={{ color: "#94a3b8" }}>
              Type: {scan.target_type}
            </Typography>
          </Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip size="small" label={String(scan.status)} color={statusChipColor(String(scan.status))} />
            <Chip size="small" label={`Progress ${scan.progress ?? 0}%`} variant="outlined" />
          </Stack>
        </Stack>

        {scan.status === "pending_approval" && user?.role === "admin" ? (
          <Box sx={{ mt: 1, display: "flex", gap: 1 }}>
            <Button
              variant="contained"
              onClick={async () => {
                await api.post(`/scans/${scan.id}/approve`);
                await load();
              }}
            >
              Approve & enqueue
            </Button>
            <Button
              variant="outlined"
              color="error"
              onClick={async () => {
                await api.post(`/scans/${scan.id}/deny`);
                await load();
              }}
            >
              Deny
            </Button>
          </Box>
        ) : null}
        <Box sx={{ mt: 1.5, display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Button variant="outlined" href={`/api/v1/reports/vapt/${scan.id}/pdf`} target="_blank">
            Download PDF
          </Button>
          <Button variant="outlined" href={`/api/v1/reports/vapt/${scan.id}/json`} target="_blank">
            Download JSON
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 2.5, bgcolor: "#0f172a", borderRadius: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1.5, fontWeight: 700 }}>
          Findings ({findings.length})
        </Typography>
        <Stack spacing={1.25}>
          {findings.map((f) => (
            <Paper key={f.id} variant="outlined" sx={{ p: 1.25, bgcolor: "#0b1324", borderColor: "#1f2a44" }}>
              <Box sx={{ display: "flex", justifyContent: "space-between", gap: 1, flexWrap: "wrap" }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {f.title}
                </Typography>
                <Stack direction="row" spacing={0.75}>
                  <Chip
                    size="small"
                    label={String(f.severity ?? "unknown")}
                    color={severityChipColor(String(f.severity ?? ""))}
                  />
                  <Chip size="small" label={String(f.tool ?? "tool")} variant="outlined" />
                </Stack>
              </Box>
              {f.cve_id ? (
                <Typography variant="caption" sx={{ color: "#94a3b8" }}>
                  CVE: {f.cve_id} • CVSS: {f.cvss_score ?? "-"}
                </Typography>
              ) : null}
            </Paper>
          ))}
        </Stack>
      </Paper>
    </Box>
  );
}

