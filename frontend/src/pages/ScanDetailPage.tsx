import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Box, Button, Paper, Typography } from "@mui/material";
import { api } from "../api/client";
import { useAuth } from "../state/AuthProvider";

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
        Scan #{scan.id}
      </Typography>

      <Paper sx={{ p: 2, bgcolor: "#0f172a", mb: 2 }}>
        <Typography variant="body2">
          Target: <b>{scan.target}</b> ({scan.target_type})
        </Typography>
        <Typography variant="body2">
          Status: <b>{scan.status}</b> • Progress: <b>{scan.progress}%</b>
        </Typography>
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
        <Box sx={{ mt: 1, display: "flex", gap: 1 }}>
          <Button variant="outlined" href={`/api/v1/reports/vapt/${scan.id}/pdf`} target="_blank">
            Download PDF
          </Button>
          <Button variant="outlined" href={`/api/v1/reports/vapt/${scan.id}/json`} target="_blank">
            Download JSON
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 2, bgcolor: "#0f172a" }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Findings ({findings.length})
        </Typography>
        {findings.map((f) => (
          <Box key={f.id} sx={{ py: 1, borderBottom: "1px solid #1f2a44" }}>
            <Typography variant="body2">
              [{f.severity}] {f.title} <span style={{ color: "#94a3b8" }}>({f.tool})</span>
            </Typography>
            {f.cve_id ? (
              <Typography variant="caption" sx={{ color: "#94a3b8" }}>
                CVE: {f.cve_id} • CVSS: {f.cvss_score ?? "—"}
              </Typography>
            ) : null}
          </Box>
        ))}
      </Paper>
    </Box>
  );
}

