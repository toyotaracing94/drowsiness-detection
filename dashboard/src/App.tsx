import React, { useState } from "react";
import { Box, Toolbar } from "@mui/material";
import AppHeader from "./components/AppHeader";
import SideBarNavigation from "./components/SideBarNavigation";
import DashboardPage from "./pages/DashboardPage";
import { Route, Routes } from "react-router-dom";

const drawerWidth = 240;

const App: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleDrawerClose = () => setDrawerOpen(false);
  const toggleDrawer = () => setDrawerOpen(prev => !prev);

  return (
    <Box>
      <SideBarNavigation
        open={drawerOpen}
        onClose={handleDrawerClose}
        drawerWidth={drawerWidth}
      />

      <Box sx={{ display: 'flex' }}>
        <AppHeader
          drawerOpen={drawerOpen}
          onDrawerToggle={toggleDrawer}
          drawerWidth={drawerWidth}
        />

        <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              marginLeft: drawerOpen ? `${drawerWidth}px` : 0,
              transition: 'margin 0.3s ease',
            }}
          >
          <Toolbar />
          <Routes>
            <Route path="/" element={<DashboardPage />} />
          </Routes>
        </Box>
        
      </Box>
    </Box>
  );
};

export default App;
