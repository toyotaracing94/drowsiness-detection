import { Sidebar, Menu, MenuItem } from 'react-pro-sidebar';
import { Link, useLocation } from 'react-router-dom';

import DashboardCustomizeOutlinedIcon from '@mui/icons-material/DashboardCustomizeOutlined';
import CalendarViewMonthOutlinedIcon from '@mui/icons-material/CalendarViewMonthOutlined';
import React from 'react';
import { Box } from '@mui/material';

const SideBarNavigation: React.FC<{collapsed: boolean}> = ({ collapsed }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar style={{top:'auto'}} collapsed={collapsed} breakPoint='xl' toggled={!collapsed}>
        <Menu>
          <MenuItem active={isActive('/')} component={<Link to="/" />} icon={<DashboardCustomizeOutlinedIcon/>}> Dashboard</MenuItem>
          <MenuItem active={isActive('/gallery')} component={<Link to="/gallery" />} icon={<CalendarViewMonthOutlinedIcon/>}> Event Gallery</MenuItem>
        </Menu>
      </Sidebar>
    </Box>
  );
};

export default SideBarNavigation;