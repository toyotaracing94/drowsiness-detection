import React from 'react';
import {
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar
} from '@mui/material';
import { NavLink } from 'react-router-dom';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import CollectionsIcon from '@mui/icons-material/Collections';

interface SideBarNavigationProps {
  open: boolean;
  onClose: () => void;
  drawerWidth: number;
}

const SideBarNavigation: React.FC<SideBarNavigationProps> = ({
  open,
  onClose,
  drawerWidth,
}) => {
  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar>
        <IconButton onClick={onClose}>
          <ChevronLeftIcon />
        </IconButton>
      </Toolbar>
      <Divider />
      
      <List>
        <ListItem disablePadding>
          <ListItemButton component={NavLink} to="/" onClick={onClose}>
            <ListItemIcon>
              <InboxIcon />
            </ListItemIcon>
            <ListItemText primary="Dashboard" />
          </ListItemButton>
        </ListItem>

        <ListItem disablePadding>
          <ListItemButton component={NavLink} to="/event-gallery" onClick={onClose}>
            <ListItemIcon>
              <CollectionsIcon />
            </ListItemIcon>
            <ListItemText primary="Event Gallery" />
          </ListItemButton>
        </ListItem>
      </List>

    </Drawer>
  );
};

export default SideBarNavigation;
