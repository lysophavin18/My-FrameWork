import React from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { AppBar, Box, Button, Container, Toolbar, Typography } from "@mui/material";
import { useAuth } from "../state/AuthProvider";
import AIChatWidget from "./AIChatWidget";

export default function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#0a0e27" }}>
      <AppBar 
        position="static" 
        sx={{ 
          bgcolor: "#12192f",
          borderBottom: "1px solid rgba(59, 130, 246, 0.1)",
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.2)"
        }}
      >
        <Toolbar sx={{ py: 1.5 }}>
          <Typography 
            variant="h5" 
            sx={{ 
              flexGrow: 1, 
              fontWeight: 700,
              background: "linear-gradient(90deg, #3b82f6, #f59e0b)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              letterSpacing: "-0.5px"
            }}
          >
            Expl0V1N
          </Typography>
          
          <Box sx={{ display: "flex", gap: 0.5 }}>
            <Button 
              color="inherit" 
              component={Link} 
              to="/"
              sx={{ 
                fontSize: "13px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                "&:hover": { bgcolor: "rgba(59, 130, 246, 0.1)" }
              }}
            >
              Dashboard
            </Button>
            <Button 
              color="inherit" 
              component={Link} 
              to="/scans"
              sx={{ 
                fontSize: "13px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                "&:hover": { bgcolor: "rgba(59, 130, 246, 0.1)" }
              }}
            >
              VAPT
            </Button>
            <Button 
              color="inherit" 
              component={Link} 
              to="/hunting"
              sx={{ 
                fontSize: "13px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                "&:hover": { bgcolor: "rgba(59, 130, 246, 0.1)" }
              }}
            >
              Recon
            </Button>
            <Button 
              color="inherit" 
              component={Link} 
              to="/settings"
              sx={{ 
                fontSize: "13px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                "&:hover": { bgcolor: "rgba(59, 130, 246, 0.1)" }
              }}
            >
              Settings
            </Button>
          </Box>

          <Box sx={{ ml: 3, display: "flex", alignItems: "center", gap: 2 }}>
            <Typography 
              variant="caption" 
              sx={{ 
                color: "#b0bec5",
                fontWeight: 600,
                borderRight: "1px solid #1f3454",
                paddingRight: 2
              }}
            >
              {user?.email.split("@")[0]} • {user?.role.toUpperCase()}
            </Typography>
            <Button
              color="inherit"
              onClick={() => {
                logout();
                navigate("/login");
              }}
              sx={{ 
                fontSize: "12px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                color: "#ef4444",
                "&:hover": { bgcolor: "rgba(239, 68, 68, 0.1)" }
              }}
            >
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container sx={{ py: 3 }}>
        <Outlet />
      </Container>

      <AIChatWidget />
    </Box>
  );
}

