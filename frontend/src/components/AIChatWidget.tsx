import React, { useMemo, useState } from "react";
import { Box, Button, Paper, TextField, Typography } from "@mui/material";
import { api } from "../api/client";

type Msg = { role: "user" | "assistant"; content: string };

export default function AIChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  const containerSx = useMemo(
    () => ({
      position: "fixed" as const,
      right: 20,
      bottom: 20,
      width: open ? 360 : 160,
      zIndex: 1300,
    }),
    [open]
  );

  async function send() {
    const text = input.trim();
    if (!text) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setBusy(true);
    try {
      const resp = await api.post("/ai/chat", { message: text });
      setMessages((m) => [...m, { role: "assistant", content: resp.data.message }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "AI service unavailable." }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Box sx={containerSx}>
      {!open ? (
        <Button variant="contained" onClick={() => setOpen(true)} fullWidth>
          AI Assistant
        </Button>
      ) : (
        <Paper sx={{ p: 2, bgcolor: "#0f172a", color: "#e2e8f0" }} elevation={8}>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <Typography variant="subtitle2">AI Assistant</Typography>
            <Button size="small" onClick={() => setOpen(false)}>
              Close
            </Button>
          </Box>
          <Box sx={{ mt: 1, height: 240, overflow: "auto", pr: 1 }}>
            {messages.length === 0 ? (
              <Typography variant="caption" sx={{ color: "#94a3b8" }}>
                Ask about findings, prioritization, or remediation.
              </Typography>
            ) : (
              messages.map((m, idx) => (
                <Box key={idx} sx={{ mb: 1 }}>
                  <Typography variant="caption" sx={{ color: "#94a3b8" }}>
                    {m.role}
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                    {m.content}
                  </Typography>
                </Box>
              ))
            )}
          </Box>
          <Box sx={{ mt: 1, display: "flex", gap: 1 }}>
            <TextField
              size="small"
              fullWidth
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask something..."
              sx={{ input: { color: "#e2e8f0" } }}
            />
            <Button variant="contained" disabled={busy} onClick={send}>
              Send
            </Button>
          </Box>
        </Paper>
      )}
    </Box>
  );
}

