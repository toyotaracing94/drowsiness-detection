import React from "react";
import { AppBar, Box, IconButton, Toolbar, Typography, useMediaQuery } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { useTheme } from "@mui/material/styles";

interface AppHeaderProps {
  drawerOpen: boolean;
  onDrawerToggle: () => void;
  drawerWidth: number;
}

const AppHeader: React.FC<AppHeaderProps> = ({ drawerOpen, onDrawerToggle, drawerWidth }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm')); // sm = <600px

  return (
    <Box>
      <AppBar
        position="fixed"
        sx={{
          width: !isMobile && drawerOpen ? `calc(100% - ${drawerWidth}px)` : '100%',
          ml: !isMobile && drawerOpen ? `${drawerWidth}px` : 0,
          transition: 'width 0.3s ease, margin 0.3s ease',
          p: 0.7,
        }}
      >
        <Toolbar>
          {!drawerOpen && (
            <IconButton
              color="inherit"
              edge="start"
              onClick={onDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon sx={{ fontSize: 38 }} />
            </IconButton>
          )}

          <Box display="flex" alignItems="center">
            <Box
              component="img"
              src="src/assets/logo_drivesafepi.png"
              sx={{ width: 65, mr: 2 }}
            />
            <Box>
              <Typography variant="h4">DriveSafePi</Typography>
              <Typography variant="body2">
                Drowsiness Detection System Internal Dashboard on Raspberry Pi 5
              </Typography>
            </Box>
          </Box>
        </Toolbar>
      </AppBar>
    </Box>
  );
};

export default AppHeader;
