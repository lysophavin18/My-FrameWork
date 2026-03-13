import React, { useEffect, useState } from "react";
import { Box, Button, Paper, Switch, TextField, Typography } from "@mui/material";
import { api } from "../api/client";

export default function SettingsPage() {
  const [cfg, setCfg] = useState<any | null>(null);
  const [busy, setBusy] = useState(false);

  async function load() {
    try {
      const resp = await api.get("/notifications/config");
      setCfg(resp.data);
    } catch {
      setCfg({ enabled: false, provider: "telegram", bot_token: "", chat_id: "" });
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (!cfg) return null;

  return (
    <Box sx={{ color: "#e2e8f0" }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Settings
      </Typography>

      <Paper sx={{ p: 2, bgcolor: "#0f172a" }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Telegram notifications
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
          <Switch
            checked={!!cfg.enabled}
            onChange={(e) => setCfg((c: any) => ({ ...c, enabled: e.target.checked }))}
          />
          <Typography variant="body2">{cfg.enabled ? "Enabled" : "Disabled"}</Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <TextField
            label="Bot Token"
            value={cfg.bot_token ?? ""}
            onChange={(e) => setCfg((c: any) => ({ ...c, bot_token: e.target.value }))}
            sx={{ minWidth: 360, input: { color: "#e2e8f0" } }}
            InputLabelProps={{ style: { color: "#94a3b8" } }}
          />
          <TextField
            label="Chat ID"
            value={cfg.chat_id ?? ""}
            onChange={(e) => setCfg((c: any) => ({ ...c, chat_id: e.target.value }))}
            sx={{ minWidth: 220, input: { color: "#e2e8f0" } }}
            InputLabelProps={{ style: { color: "#94a3b8" } }}
          />
        </Box>
        <Box sx={{ mt: 2, display: "flex", gap: 1 }}>
          <Button
            variant="contained"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                await api.put("/notifications/config", cfg);
                await load();
              } finally {
                setBusy(false);
              }
            }}
          >
            Save
          </Button>
          <Button
            variant="outlined"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                await api.post("/notifications/test");
              } finally {
                setBusy(false);
              }
            }}
          >
            Test
          </Button>
        </Box>
        <Typography variant="caption" sx={{ color: "#94a3b8", display: "block", mt: 2 }}>
          AI Assistant configuration is set via `ai-assistant` environment variables in this scaffold.
        </Typography>
      </Paper>
    </Box>
  );
}

