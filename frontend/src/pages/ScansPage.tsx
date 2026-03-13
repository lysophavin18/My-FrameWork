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
import { api } from "../api/client";
import { Link } from "react-router-dom";
import { useAuth } from "../state/AuthProvider";

const TOOL_OPTIONS = ["nmap", "nuclei", "nikto", "zap", "sqlmap"];

function statusChipColor(status: string): "default" | "success" | "warning" | "error" | "info" {
  if (["completed", "done", "success"].includes(status)) return "success";
  if (["running", "queued", "pending", "approved"].includes(status)) return "info";
  if (["pending_approval"].includes(status)) return "warning";
  if (["failed", "denied", "error"].includes(status)) return "error";
  return "default";
}

export default function ScansPage() {
  const { user } = useAuth();
  const [scans, setScans] = useState<any[]>([]);
  const [target, setTarget] = useState("");
  const [targetType, setTargetType] = useState<"ip" | "domain" | "url">("url");
  const [selectedTools, setSelectedTools] = useState<string[]>(["nmap", "nuclei", "nikto"]);
  const [busy, setBusy] = useState(false);

  async function load() {
    const resp = await api.get("/scans/");
    setScans(resp.data);
  }

  useEffect(() => {
    load();
  }, []);

  function toggleTool(tool: string) {
    setSelectedTools((prev) => {
      if (prev.includes(tool)) {
        return prev.filter((t) => t !== tool);
      }
      return [...prev, tool];
    });
  }

  return (
    <Box sx={{ color: "#e2e8f0" }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        VAPT Tools
      </Typography>
      <Typography variant="body2" sx={{ color: "#94a3b8", mb: 2 }}>
        Launch a single-target scan with just the tools you need.
      </Typography>

      <Paper sx={{ p: 2.5, bgcolor: "#0f172a", mb: 2, borderRadius: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1.5, fontWeight: 700 }}>
          New scan request
        </Typography>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1.25} sx={{ mb: 1.5 }}>
          <TextField
            label="Target"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="example.com or https://example.com"
            sx={{ minWidth: 360, input: { color: "#e2e8f0" }, flex: 1 }}
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
        </Stack>

        <Typography variant="caption" sx={{ color: "#94a3b8", display: "block", mb: 0.75 }}>
          Select tools
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
          {TOOL_OPTIONS.map((tool) => {
            const active = selectedTools.includes(tool);
            return (
              <Chip
                key={tool}
                label={tool.toUpperCase()}
                clickable
                onClick={() => toggleTool(tool)}
                color={active ? "primary" : "default"}
                variant={active ? "filled" : "outlined"}
              />
            );
          })}
        </Stack>

        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Button
            variant="contained"
            disabled={busy || !target.trim() || selectedTools.length === 0}
            onClick={async () => {
              setBusy(true);
              try {
                await api.post("/scans/", {
                  target,
                  target_type: targetType,
                  tools_config: Object.fromEntries(selectedTools.map((tool) => [tool, true])),
                });
                setTarget("");
                await load();
              } finally {
                setBusy(false);
              }
            }}
          >
            {busy ? "Submitting..." : "Enqueue scan"}
          </Button>
        </Box>
        <Typography variant="caption" sx={{ color: "#94a3b8", mt: 1.25, display: "block" }}>
          Public targets require admin approval and allowlist. Current role: {user?.role}
        </Typography>
      </Paper>

      <Paper sx={{ p: 2.5, bgcolor: "#0f172a", borderRadius: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 1.5, fontWeight: 700 }}>
          Scan history
        </Typography>
        {scans.length === 0 ? (
          <Alert severity="info" sx={{ bgcolor: "#0b253d", color: "#dbeafe", border: "1px solid #1f2a44" }}>
            No scans yet. Create your first scan from the form above.
          </Alert>
        ) : (
          <Stack spacing={1.25}>
            {scans.map((s) => (
              <Card key={s.id} variant="outlined" sx={{ bgcolor: "#0b1324", borderColor: "#1f2a44" }}>
                <CardContent sx={{ py: "12px !important" }}>
                  <Box sx={{ display: "flex", justifyContent: "space-between", gap: 1, flexWrap: "wrap" }}>
                    <Typography variant="body2">
                      <Link to={`/scans/${s.id}`} style={{ color: "#93c5fd", textDecoration: "none" }}>
                        #{s.id}
                      </Link>{" "}
                      {s.target} ({s.target_type})
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

