import React, { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../state/AuthProvider";

const METHOD_OPTIONS = [
  "subfinder",
  "amass",
  "httpx",
  "katana",
  "ffuf",
  "gowitness",
  "nuclei",
];

function statusChipColor(status: string): "default" | "success" | "warning" | "error" | "info" {
  if (["completed", "done", "success"].includes(status)) return "success";
  if (["running", "queued", "pending", "approved"].includes(status)) return "info";
  if (["pending_approval"].includes(status)) return "warning";
  if (["failed", "denied", "error"].includes(status)) return "error";
  return "default";
}

export default function HuntingPage() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<any[]>([]);
  const [rootDomain, setRootDomain] = useState("");
  const [preset, setPreset] = useState<string>("quick");
  const [selectedMethods, setSelectedMethods] = useState<string[]>(["subfinder", "httpx", "nuclei"]);
  const [busy, setBusy] = useState(false);

  async function load() {
    const resp = await api.get("/hunting/sessions");
    setSessions(resp.data);
  }

  useEffect(() => {
    load();
  }, []);

  function toggleMethod(method: string) {
    setSelectedMethods((prev) => {
      if (prev.includes(method)) {
        return prev.filter((m) => m !== method);
      }
      return [...prev, method];
    });
  }

  return (
    <Box sx={{ color: "#e2e8f0" }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Recon Tools
      </Typography>
      <Typography variant="body2" sx={{ color: "#94a3b8", mb: 2 }}>
        Start a bug-hunting pipeline with a clear preset and only the methods you need.
      </Typography>

      <Paper sx={{ p: 2.5, bgcolor: "#0f172a", mb: 2, borderRadius: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1.5, fontWeight: 700 }}>
          New hunting pipeline
        </Typography>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1.25} sx={{ mb: 1.5 }}>
          <TextField
            label="Root domain"
            value={rootDomain}
            onChange={(e) => setRootDomain(e.target.value)}
            placeholder="example.com"
            sx={{ minWidth: 360, input: { color: "#e2e8f0" }, flex: 1 }}
            InputLabelProps={{ style: { color: "#94a3b8" } }}
          />
          <TextField
            select
            label="Preset"
            value={preset}
            onChange={(e) => setPreset(e.target.value)}
            sx={{ minWidth: 160 }}
            InputLabelProps={{ style: { color: "#94a3b8" } }}
          >
            <MenuItem value="quick">Quick</MenuItem>
            <MenuItem value="standard">Standard</MenuItem>
            <MenuItem value="deep">Deep</MenuItem>
            <MenuItem value="full_hunter">Full Hunter</MenuItem>
          </TextField>
        </Stack>

        <Typography variant="caption" sx={{ color: "#94a3b8", display: "block", mb: 0.75 }}>
          Recon methods
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
          {METHOD_OPTIONS.map((method) => {
            const active = selectedMethods.includes(method);
            return (
              <Chip
                key={method}
                label={method}
                clickable
                onClick={() => toggleMethod(method)}
                color={active ? "primary" : "default"}
                variant={active ? "filled" : "outlined"}
              />
            );
          })}
        </Stack>

        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Button
            variant="contained"
            disabled={busy || !rootDomain.trim() || selectedMethods.length === 0}
            onClick={async () => {
              setBusy(true);
              try {
                await api.post("/hunting/sessions", {
                  root_domain: rootDomain,
                  preset,
                  steps_config: {},
                  methods_config: Object.fromEntries(selectedMethods.map((method) => [method, true])),
                });
                setRootDomain("");
                await load();
              } finally {
                setBusy(false);
              }
            }}
          >
            {busy ? "Submitting..." : "Start"}
          </Button>
        </Box>
        <Typography variant="caption" sx={{ color: "#94a3b8", mt: 1.25, display: "block" }}>
          Public domains require admin approval and allowlist. Current role: {user?.role}
        </Typography>
      </Paper>

      <Paper sx={{ p: 2.5, bgcolor: "#0f172a", borderRadius: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1.5, fontWeight: 700 }}>
          Session history
        </Typography>
        {sessions.length === 0 ? (
          <Alert severity="info" sx={{ bgcolor: "#0b253d", color: "#dbeafe", border: "1px solid #1f2a44" }}>
            No sessions yet. Create your first hunting session from the form above.
          </Alert>
        ) : (
          <Stack spacing={1.25}>
            {sessions.map((s) => (
              <Card key={s.id} variant="outlined" sx={{ bgcolor: "#0b1324", borderColor: "#1f2a44" }}>
                <CardContent sx={{ py: "12px !important" }}>
                  <Box sx={{ display: "flex", justifyContent: "space-between", gap: 1, flexWrap: "wrap" }}>
                    <Typography variant="body2">
                      <Link to={`/hunting/${s.id}`} style={{ color: "#93c5fd", textDecoration: "none" }}>
                        #{s.id}
                      </Link>{" "}
                      {s.root_domain}
                    </Typography>
                    <Chip size="small" label={String(s.status)} color={statusChipColor(String(s.status))} />
                  </Box>
                  <Box sx={{ mt: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={Number(s.progress ?? 0)}
                      sx={{ bgcolor: "#18243b", borderRadius: 8, height: 8 }}
                    />
                    <Typography variant="caption" sx={{ color: "#94a3b8", mt: 0.5, display: "block" }}>
                      Progress: {s.progress ?? 0}%
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Stack>
        )}
      </Paper>
    </Box>
  );
}

