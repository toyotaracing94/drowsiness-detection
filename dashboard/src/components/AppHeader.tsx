import React from "react";
import { AppBar, Box, IconButton, Toolbar, Typography } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";

const AppHeader: React.FC<{ collapsed : boolean ,setCollapsed: (value: boolean) => void }> = ({ collapsed, setCollapsed }) => {

  const handleSidebarToggle = () => {
    setCollapsed(!collapsed);
  }

  return (
    <AppBar position="sticky" sx={{paddingY:0.8}}>
      <Toolbar disableGutters sx={{paddingLeft: '12px'}}>

        <IconButton onClick={handleSidebarToggle} color="inherit" size="large" sx={{marginRight:'24px'}}>
          <MenuIcon/>
        </IconButton>

        <Box>
          <Typography variant="h6" sx={{fontSize:'1.3em'}}>DriveSafePi</Typography>
          <Typography variant="body2" sx={{fontSize:'0.8em'}}>
            Drowsiness Detection System Internal Dashboard on Raspberry Pi 5
          </Typography>
        </Box>

      </Toolbar>
    </AppBar>
  );
};

export default AppHeader;