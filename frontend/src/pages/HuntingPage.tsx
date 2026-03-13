import React, { useEffect, useState } from "react";
import { Box, Button, MenuItem, Paper, TextField, Typography } from "@mui/material";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../state/AuthProvider";

export default function HuntingPage() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<any[]>([]);
  const [rootDomain, setRootDomain] = useState("");
  const [preset, setPreset] = useState<string>("quick");
  const [busy, setBusy] = useState(false);

  async function load() {
    const resp = await api.get("/hunting/sessions");
    setSessions(resp.data);
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <Box sx={{ color: "#e2e8f0" }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Bug Hunting (recon pipeline)
      </Typography>

      <Paper sx={{ p: 2, bgcolor: "#0f172a", mb: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          New pipeline
        </Typography>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <TextField
            label="Root domain"
            value={rootDomain}
            onChange={(e) => setRootDomain(e.target.value)}
            sx={{ minWidth: 360, input: { color: "#e2e8f0" } }}
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
          <Button
            variant="contained"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                await api.post("/hunting/sessions", {
                  root_domain: rootDomain,
                  preset,
                  steps_config: {},
                  methods_config: {},
                });
                setRootDomain("");
                await load();
              } finally {
                setBusy(false);
              }
            }}
          >
            Start
          </Button>
        </Box>
        <Typography variant="caption" sx={{ color: "#94a3b8", mt: 1, display: "block" }}>
          Public domains require admin approval and allowlist. Current role: {user?.role}
        </Typography>
      </Paper>

      <Paper sx={{ p: 2, bgcolor: "#0f172a" }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          History
        </Typography>
        {sessions.map((s) => (
          <Box
            key={s.id}
            sx={{
              display: "flex",
              justifyContent: "space-between",
              py: 1,
              borderBottom: "1px solid #1f2a44",
            }}
          >
            <Typography variant="body2">
              <Link to={`/hunting/${s.id}`} style={{ color: "#93c5fd" }}>
                #{s.id}
              </Link>{" "}
              {s.root_domain}
            </Typography>
            <Typography variant="caption" sx={{ color: "#94a3b8" }}>
              {s.status} • {s.progress}%
            </Typography>
          </Box>
        ))}
      </Paper>
    </Box>
  );
}

