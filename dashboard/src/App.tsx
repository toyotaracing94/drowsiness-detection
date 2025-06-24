import React, { useState } from "react";
import { ThemeProvider, useTheme } from '@mui/material/styles';
import { Box, CssBaseline, Toolbar, useMediaQuery } from "@mui/material";
import AppHeader from "./components/AppHeader";
import SideBarNavigation from "./components/SideBarNavigation";
import DashboardPage from "./pages/DashboardPage";
import { Route, Routes } from "react-router-dom";
import theme from "./config/theme";

const drawerWidth = 240;

const App: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const handleDrawerClose = () => setDrawerOpen(false);
  const toggleDrawer = () => setDrawerOpen(prev => !prev);

  const muiTheme = useTheme(); // hook from material
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('sm'));

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      
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
            marginLeft: !isMobile && drawerOpen ? `${drawerWidth}px` : 0,
            transition: 'margin 0.2s ease',
          }}
        >
          <Toolbar />
          <Routes>
            <Route path="/" element={<DashboardPage />} />
          </Routes>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default App;
