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

      <Paper sx={{ p: 2.5, bgcolor: "#0f172a", mb: 2, borderRadius: 3 }}>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1.5} justifyContent="space-between" sx={{ mb: 1 }}>
          <Box>
            <Typography variant="caption" sx={{ color: "#94a3b8" }}>
              Root domain
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 700 }}>
              {session.root_domain}
            </Typography>
            <Typography variant="caption" sx={{ color: "#94a3b8" }}>
              Step: {session.current_step ?? "-"}
            </Typography>
          </Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip size="small" label={String(session.status)} color={statusChipColor(String(session.status))} />
            <Chip size="small" label={`Progress ${session.progress ?? 0}%`} variant="outlined" />
          </Stack>
        </Stack>

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
        <Box sx={{ mt: 1.5, display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Button variant="outlined" href={`/api/v1/reports/hunting/${session.id}/pdf`} target="_blank">
            Download PDF
          </Button>
          <Button variant="outlined" href={`/api/v1/reports/hunting/${session.id}/json`} target="_blank">
            Download JSON
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 2.5, bgcolor: "#0f172a", mb: 2, borderRadius: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1.25, fontWeight: 700 }}>
          Subdomains ({subdomains.length})
        </Typography>
        <Box sx={{ maxHeight: 180, overflow: "auto" }}>
          {subdomains.map((s) => (
            <Paper
              key={s.id}
              variant="outlined"
              sx={{ p: 1, mb: 0.75, bgcolor: "#0b1324", borderColor: "#1f2a44", fontFamily: "monospace" }}
            >
              <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
                {s.subdomain}
              </Typography>
            </Paper>
          ))}
        </Box>
      </Paper>

      <Paper sx={{ p: 2.5, bgcolor: "#0f172a", mb: 2, borderRadius: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1.25, fontWeight: 700 }}>
          Live hosts ({liveHosts.length})
        </Typography>
        <Box sx={{ maxHeight: 180, overflow: "auto" }}>
          {liveHosts.map((h) => (
            <Paper
              key={h.id}
              variant="outlined"
              sx={{ p: 1, mb: 0.75, bgcolor: "#0b1324", borderColor: "#1f2a44", fontFamily: "monospace" }}
            >
              <Typography key={h.id} variant="body2" sx={{ fontFamily: "monospace" }}>
                {h.url} {h.status_code ? `(${h.status_code})` : ""}
              </Typography>
            </Paper>
          ))}
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
              {f.url ? (
                <Typography variant="caption" sx={{ color: "#94a3b8" }}>
                  {f.url}
                </Typography>
              ) : null}
            </Paper>
          ))}
        </Stack>
      </Paper>
    </Box>
  );
}

