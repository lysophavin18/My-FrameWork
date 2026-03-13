import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Box, Button, Paper, Typography } from "@mui/material";
import { api } from "../api/client";
import { useAuth } from "../state/AuthProvider";

export default function HuntingDetailPage() {
  const { sessionId } = useParams();
  const { user } = useAuth();
  const [session, setSession] = useState<any | null>(null);
  const [subdomains, setSubdomains] = useState<any[]>([]);
  const [liveHosts, setLiveHosts] = useState<any[]>([]);
  const [findings, setFindings] = useState<any[]>([]);

  async function load() {
    const s = await api.get(`/hunting/sessions/${sessionId}`);
    setSession(s.data);
    const sd = await api.get(`/hunting/sessions/${sessionId}/subdomains`);
    setSubdomains(sd.data);
    const lh = await api.get(`/hunting/sessions/${sessionId}/live-hosts`);
    setLiveHosts(lh.data);
    const f = await api.get(`/hunting/sessions/${sessionId}/findings`);
    setFindings(f.data);
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, [sessionId]);

  if (!session) return null;

  return (
    <Box sx={{ color: "#e2e8f0" }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Hunting session #{session.id}
      </Typography>

      <Paper sx={{ p: 2, bgcolor: "#0f172a", mb: 2 }}>
        <Typography variant="body2">
          Root domain: <b>{session.root_domain}</b>
        </Typography>
        <Typography variant="body2">
          Status: <b>{session.status}</b> • Progress: <b>{session.progress}%</b> • Step:{" "}
          {session.current_step ?? "—"}
        </Typography>
        {session.status === "pending_approval" && user?.role === "admin" ? (
          <Box sx={{ mt: 1, display: "flex", gap: 1 }}>
            <Button
              variant="contained"
              onClick={async () => {
                await api.post(`/hunting/sessions/${session.id}/approve`);
                await load();
              }}
            >
              Approve & start
            </Button>
            <Button
              variant="outlined"
              color="error"
              onClick={async () => {
                await api.post(`/hunting/sessions/${session.id}/deny`);
                await load();
              }}
            >
              Deny
            </Button>
          </Box>
        ) : null}
        <Box sx={{ mt: 1, display: "flex", gap: 1 }}>
          <Button variant="outlined" href={`/api/v1/reports/hunting/${session.id}/pdf`} target="_blank">
            Download PDF
          </Button>
          <Button variant="outlined" href={`/api/v1/reports/hunting/${session.id}/json`} target="_blank">
            Download JSON
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 2, bgcolor: "#0f172a", mb: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Subdomains ({subdomains.length})
        </Typography>
        <Box sx={{ maxHeight: 160, overflow: "auto" }}>
          {subdomains.map((s) => (
            <Typography key={s.id} variant="body2" sx={{ fontFamily: "monospace" }}>
              {s.subdomain}
            </Typography>
          ))}
        </Box>
      </Paper>

      <Paper sx={{ p: 2, bgcolor: "#0f172a", mb: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Live hosts ({liveHosts.length})
        </Typography>
        <Box sx={{ maxHeight: 160, overflow: "auto" }}>
          {liveHosts.map((h) => (
            <Typography key={h.id} variant="body2" sx={{ fontFamily: "monospace" }}>
              {h.url} {h.status_code ? `(${h.status_code})` : ""}
            </Typography>
          ))}
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
            {f.url ? (
              <Typography variant="caption" sx={{ color: "#94a3b8" }}>
                {f.url}
              </Typography>
            ) : null}
          </Box>
        ))}
      </Paper>
    </Box>
  );
}

