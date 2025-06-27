// components/GalleryCard.tsx
import { Card, CardMedia, CardContent, Typography } from '@mui/material';
import React from 'react';
import { API_URL_LOCATION } from '../constant/urlConstant';

interface EventData {
  id: string;
  image: string;
  timestamp: string;
  event_type: string;
  mar: number;
  ear: number;
  vehicle_identification: string;
}

const GalleryCard: React.FC<{ event: EventData }> = ({ event }) => {
  return (
    <Card sx={{ maxWidth: 345 }}>
      <CardMedia
        component="img"
        height="200"
        image={`${API_URL_LOCATION}/${event.image}`}
        alt={event.event_type}
      />
      <CardContent>
        <Typography variant="h6">{event.event_type}</Typography>
        <Typography variant="body2" color="text.secondary">
          Time: {new Date(event.timestamp).toLocaleString()}
        </Typography>
        <Typography variant="body2">EAR: {event.ear.toFixed(2)}</Typography>
        <Typography variant="body2">MAR: {event.mar.toFixed(2)}</Typography>
      </CardContent>
    </Card>
  );
};

export default GalleryCard;