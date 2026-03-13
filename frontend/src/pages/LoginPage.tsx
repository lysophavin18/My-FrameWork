import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Alert, Box, Button, Paper, TextField, Typography } from "@mui/material";
import { useAuth } from "../state/AuthProvider";

export default function LoginPage() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "#0b1220",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        p: 2,
      }}
    >
      <Paper sx={{ p: 4, width: 420, bgcolor: "#0f172a", color: "#e2e8f0" }} elevation={10}>
        <Typography variant="h5">Expl0V1N</Typography>
        <Typography variant="body2" sx={{ color: "#94a3b8", mt: 0.5 }}>
          Sign in to run authorized scans
        </Typography>
        {error ? (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        ) : null}
        <Box sx={{ mt: 3, display: "flex", flexDirection: "column", gap: 2 }}>
          <TextField
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            fullWidth
            InputLabelProps={{ style: { color: "#94a3b8" } }}
            sx={{ input: { color: "#e2e8f0" } }}
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            fullWidth
            InputLabelProps={{ style: { color: "#94a3b8" } }}
            sx={{ input: { color: "#e2e8f0" } }}
          />
          <Button
            variant="contained"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              setError(null);
              try {
                await login(email, password);
                nav("/");
              } catch {
                setError("Login failed");
              } finally {
                setBusy(false);
              }
            }}
          >
            Login
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}

