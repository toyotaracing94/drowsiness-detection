import React from "react";
import { AppBar, Box, IconButton, Toolbar, Typography } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";

interface AppHeaderProps {
  drawerOpen: boolean;
  onDrawerToggle: () => void;
  drawerWidth: number;
}

const AppHeader: React.FC<AppHeaderProps> = ({ drawerOpen, onDrawerToggle, drawerWidth }) => {
  return (
    <Box>
        <AppBar
        sx={{
            width: drawerOpen ? `calc(100% - ${drawerWidth}px)` : '100%',
            ml: drawerOpen ? `${drawerWidth}px` : 0,
            transition: 'width 0.3s ease, margin 0.3s ease',
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
                <MenuIcon />
            </IconButton>
            )}
            <Box>
            <Typography variant="h6">DriveSafePi</Typography>
            <Typography variant="body2">
                Drowsiness Detection System Internal Dashboard on Raspberry Pi 5
            </Typography>
            </Box>
        </Toolbar>

        </AppBar>
    </Box>
  );
};

export default AppHeader;
