import React from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { AppBar, Box, Button, Container, Toolbar, Typography } from "@mui/material";
import { useAuth } from "../state/AuthProvider";
import AIChatWidget from "./AIChatWidget";

export default function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#0b1220" }}>
      <AppBar position="static" sx={{ bgcolor: "#0f172a" }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Expl0V1N
          </Typography>
          <Button color="inherit" component={Link} to="/">
            Dashboard
          </Button>
          <Button color="inherit" component={Link} to="/scans">
            VAPT
          </Button>
          <Button color="inherit" component={Link} to="/hunting">
            Bug Hunting
          </Button>
          <Button color="inherit" component={Link} to="/settings">
            Settings
          </Button>
          <Box sx={{ ml: 2 }}>
            <Typography variant="caption" sx={{ color: "#cbd5e1" }}>
              {user?.email} ({user?.role})
            </Typography>
          </Box>
          <Button
            color="inherit"
            onClick={() => {
              logout();
              navigate("/login");
            }}
            sx={{ ml: 2 }}
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container sx={{ py: 3 }}>
        <Outlet />
      </Container>

      <AIChatWidget />
    </Box>
  );
}

