import { Sidebar, Menu, MenuItem } from 'react-pro-sidebar';
import { Link, useLocation } from 'react-router-dom';

import DashboardCustomizeOutlinedIcon from '@mui/icons-material/DashboardCustomizeOutlined';
import CalendarViewMonthOutlinedIcon from '@mui/icons-material/CalendarViewMonthOutlined';
import React from 'react';

const SideBarNavigation: React.FC<{collapsed: boolean}> = ({ collapsed }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <Sidebar style={{height : '100vh', top:'auto'}} collapsed={collapsed} breakPoint='xl' toggled={!collapsed}>
      <Menu>
        <MenuItem active={isActive('/')} component={<Link to="/" />} icon={<DashboardCustomizeOutlinedIcon/>}> Dashboard</MenuItem>
        <MenuItem active={isActive('/event-gallery')} component={<Link to="/event-gallery" />} icon={<CalendarViewMonthOutlinedIcon/>}> Event Gallery</MenuItem>
      </Menu>
    </Sidebar>
  );
};

export default SideBarNavigation;