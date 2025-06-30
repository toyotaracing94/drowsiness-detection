import React, { useState } from "react";
import { ThemeProvider } from '@mui/material/styles';
import { Box, CssBaseline } from "@mui/material";
import AppHeader from "./components/AppHeader";
import SideBarNavigation from "./components/SideBarNavigation";
import DashboardPage from "./pages/DashboardPage";
import { Route, Routes } from "react-router-dom";
import theme from "./config/theme";
import NotFoundPage from "./pages/NotFoundPage";
import EventGalleryPage from "./pages/EventGalleryPage";

  const App: React.FC = () => {
    const [drawerOpen, setDrawerOpen] = useState(true);
    return (
    <React.Fragment>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box>
          <AppHeader collapsed={drawerOpen} setCollapsed={setDrawerOpen}/>
          <Box component="main" sx={{display: 'flex', gap: 2}}>
            <SideBarNavigation collapsed={drawerOpen}/>
            <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/gallery" element={<EventGalleryPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </Box>
          </Box>
        </Box>
      </ThemeProvider>
    </React.Fragment>
    );
  };

  export default App;