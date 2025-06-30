import React from 'react';
import {
  Card,
  CardMedia,
  CardContent,
  Typography,
  Box,
  Chip,
  Stack,
  Tooltip,
} from '@mui/material';
import { API_URL_LOCATION } from '../constant/urlConstant';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import TimelineIcon from '@mui/icons-material/Timeline';
import moment from 'moment';

interface EventData {
  id: string;
  image: string;
  timestamp: string;
  event_type: string;
  mar: number;
  ear: number;
  vehicle_identification: string;
}

const GalleryCard: React.FC<{ event: EventData; onClick?: () => void }> = ({ event, onClick }) => {
  return (
    <Card 
      variant="outlined"
      sx={{
        maxWidth: 400,
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)'
        },
        cursor:'pointer'
      }}
      onClick={onClick}
    >
      <CardMedia
        component="img"
        height="250"
        image={`${API_URL_LOCATION}/${event.image}`}
        alt={event.event_type}
        sx={{ objectFit: 'fill'}}
      />

      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Chip label={event.event_type} color="primary" size="small" />
          <Tooltip title="Vehicle ID">
            <Box display="flex" alignItems="center" gap={0.5}>
              <Typography variant="caption">{event.vehicle_identification}</Typography>
            </Box>
          </Tooltip>
        </Box>

        <Stack direction="row" spacing={1} alignItems="center" mb={1}>
          <AccessTimeIcon fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary">
            {moment(event.timestamp).format('dddd, MMMM Do YYYY, HH:mm:ss')}
          </Typography>
        </Stack>

        <Stack direction="row" spacing={2}>
          <Stack direction="row" spacing={0.5} alignItems="center">
            <TimelineIcon fontSize="small" color="secondary" />
            <Typography variant="body2">EAR: {event.ear.toFixed(2)}</Typography>
          </Stack>
          <Stack direction="row" spacing={0.5} alignItems="center">
            <TimelineIcon fontSize="small" color="success" />
            <Typography variant="body2">MAR: {event.mar.toFixed(2)}</Typography>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default GalleryCard;