import React, { useEffect, useState } from "react";
import { Box, Button, MenuItem, Paper, TextField, Typography } from "@mui/material";
import { api } from "../api/client";
import { Link } from "react-router-dom";
import { useAuth } from "../state/AuthProvider";

export default function ScansPage() {
  const { user } = useAuth();
  const [scans, setScans] = useState<any[]>([]);
  const [target, setTarget] = useState("");
  const [targetType, setTargetType] = useState<"ip" | "domain" | "url">("url");
  const [busy, setBusy] = useState(false);

  async function load() {
    const resp = await api.get("/scans/");
    setScans(resp.data);
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <Box sx={{ color: "#e2e8f0" }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        VAPT Scans (single target)
      </Typography>

      <Paper sx={{ p: 2, bgcolor: "#0f172a", mb: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          New scan
        </Typography>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <TextField
            label="Target"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            sx={{ minWidth: 360, input: { color: "#e2e8f0" } }}
            InputLabelProps={{ style: { color: "#94a3b8" } }}
          />
          <TextField
            select
            label="Type"
            value={targetType}
            onChange={(e) => setTargetType(e.target.value as any)}
            sx={{ minWidth: 160 }}
            InputLabelProps={{ style: { color: "#94a3b8" } }}
          >
            <MenuItem value="ip">IP</MenuItem>
            <MenuItem value="domain">Domain</MenuItem>
            <MenuItem value="url">URL</MenuItem>
          </TextField>
          <Button
            variant="contained"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                await api.post("/scans/", { target, target_type: targetType, tools_config: {} });
                setTarget("");
                await load();
              } finally {
                setBusy(false);
              }
            }}
          >
            Enqueue scan
          </Button>
        </Box>
        <Typography variant="caption" sx={{ color: "#94a3b8", mt: 1, display: "block" }}>
          Public targets require admin approval and allowlist. Current role: {user?.role}
        </Typography>
      </Paper>

      <Paper sx={{ p: 2, bgcolor: "#0f172a" }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          History
        </Typography>
        {scans.map((s) => (
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
              <Link to={`/scans/${s.id}`} style={{ color: "#93c5fd" }}>
                #{s.id}
              </Link>{" "}
              {s.target} ({s.target_type})
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

