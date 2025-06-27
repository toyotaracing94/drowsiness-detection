import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, Grid, CircularProgress } from '@mui/material';
import GalleryCard from '../components/GalleryCard';
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

const ITEMS_PER_BATCH = 10;

const EventGalleryPage: React.FC = () => {
  const [events, setEvents] = useState<EventData[]>([]);
  const [visibleCount, setVisibleCount] = useState(ITEMS_PER_BATCH);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get(`${API_URL_LOCATION}/drowsinessevent`)
      .then(response => setEvents(response.data))
      .catch(err => console.error('Failed to fetch events:', err));
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.innerHeight + document.documentElement.scrollTop;
      const nearBottom = document.documentElement.offsetHeight - 100;

      if (scrollPosition >= nearBottom && !loading && visibleCount < events.length) {
        setLoading(true);
        setTimeout(() => {
          setVisibleCount(prev => Math.min(prev + ITEMS_PER_BATCH, events.length));
          setLoading(false);
        }, 500);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [events.length, loading, visibleCount]);

  return (
    <Box sx={{ p: 4 }}>
      <Grid container spacing={2}>
        {events.slice(0, visibleCount).map(event => (
          <Grid size={{xs:12, sm:6, md:4, lg:3 }} key={event.id}>
            <GalleryCard event={event} />
          </Grid>
        ))}
      </Grid>
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      )}
    </Box>
  );
};

export default EventGalleryPage;