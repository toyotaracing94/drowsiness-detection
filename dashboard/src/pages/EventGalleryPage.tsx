import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Box,
  Grid,
  TextField,
  Button,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Alert,
} from '@mui/material';
import GalleryCard from '../components/GalleryCard';
import { API_URL_LOCATION } from '../constant/urlConstant';
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

const ITEMS_PER_BATCH = 10;

const EventGalleryPage: React.FC = () => {
  const [events, setEvents] = useState<EventData[]>([]);
  const [visibleCount, setVisibleCount] = useState(ITEMS_PER_BATCH);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedEvent, setSelectedEvent] = useState<EventData | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Snackbar state
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'warning' | 'info',
  });

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'warning' | 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const handleStartDateChange = (event: React.ChangeEvent<HTMLInputElement>) => setStartDate(event.target.value);
  const handleEndDateChange = (event: React.ChangeEvent<HTMLInputElement>) => setEndDate(event.target.value);

  const handleApplyFilter = () => {
    if (!startDate || !endDate) {
      axios
        .get(`${API_URL_LOCATION}/drowsinessevent`)
        .then((response) => setEvents(response.data))
        .catch((err) => console.error('Failed to fetch events:', err));
      return;
    }

    setLoading(true);

    axios
      .get(`${API_URL_LOCATION}/drowsinessevent`)
      .then((response) => {
        const fetchedEvents = response.data;
        const start = new Date(startDate);
        const end = new Date(endDate);
        end.setHours(23, 59, 59, 999);

        const filtered = fetchedEvents.filter((event: EventData) => {
          const eventDate = new Date(event.timestamp);
          return eventDate >= start && eventDate <= end;
        });

        setEvents(filtered);
        setVisibleCount(ITEMS_PER_BATCH);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch events:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.innerHeight + document.documentElement.scrollTop;
      const nearBottom = document.documentElement.offsetHeight - 100;

      if (scrollPosition >= nearBottom && !loading && visibleCount < events.length) {
        setLoading(true);
        setTimeout(() => {
          setVisibleCount((prev) => Math.min(prev + ITEMS_PER_BATCH, events.length));
          setLoading(false);
        }, 500);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [events.length, loading, visibleCount]);

  const handleCardClick = (event: EventData) => {
    setSelectedEvent(event);
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setSelectedEvent(null);
    setIsDialogOpen(false);
  };

  const handleDownload = async () => {
    if (!selectedEvent) {
      showSnackbar('No event selected.', 'warning');
      return;
    }
    const url = `${API_URL_LOCATION}/drowsinessevent/download/${selectedEvent.id}`;

    try {
      const response = await axios.get(url, {
        responseType: 'blob',
      });

      if (response.status === 200) {
        const contentDisposition = response.headers['content-disposition'];
        const filename = contentDisposition
          ? contentDisposition.split('filename=')[1].replace(/"/g, '')
          : 'download.png';

        const blob = response.data;
        const link = document.createElement('a');
        const blobUrl = window.URL.createObjectURL(new Blob([blob]));
        link.href = blobUrl;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(blobUrl);

        showSnackbar('Download successful!', 'success');
      } else {
        throw new Error('Failed to download the image');
      }
    } catch (error) {
      console.error('Error during file download:', error);
      showSnackbar(`${(error as Error).message}`, 'error');
    }
  };

  return (
    <Box sx={{ p: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid size={{xs : 12, sm : 4}}>
            <TextField
              label="Start Date"
              type="date"
              fullWidth
              value={startDate}
              onChange={handleStartDateChange}
              slotProps={{ inputLabel: { shrink: true } }}
              sx={{ cursor: 'pointer' }}
            />
          </Grid>
          <Grid size={{xs : 12, sm : 4}}>
            <TextField
              label="End Date"
              type="date"
              fullWidth
              value={endDate}
              onChange={handleEndDateChange}
              slotProps={{ inputLabel: { shrink: true } }}
            />
          </Grid>
          <Grid size={{xs : 12, sm : 4}} sx={{ display: 'flex' }}>
            <Button variant="contained" color="primary" onClick={handleApplyFilter} fullWidth>
              Apply Filter
            </Button>
          </Grid>
        </Grid>
      </Box>

      <Grid container spacing={2} sx={{ alignItems: 'center' }}>
        {events.length === 0 && !loading && (
          <Box
            sx={{
              textAlign: 'center',
              color: 'text.secondary',
            }}
          >
            <Box component="p" sx={{ fontSize: '1.1rem' }}>
              No events found for the selected date range.
            </Box>
          </Box>
        )}

        {events.slice(0, visibleCount).map((event) => (
          <Grid size={{xs:12, sm:6, md:4, lg:3}} key={event.id}>
            <GalleryCard event={event} onClick={() => handleCardClick(event)} />
          </Grid>
        ))}
      </Grid>

      {loading && (
        <Box sx={{ display: 'flex', mt: 4 }}>
          <CircularProgress />
        </Box>
      )}

      <Dialog open={isDialogOpen} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        {selectedEvent && (
          <>
            <DialogTitle sx={{ fontWeight: 800 }}>{selectedEvent.event_type}</DialogTitle>
            <DialogContent>
              <Box
                component="img"
                src={`${API_URL_LOCATION}/${selectedEvent.image}`}
                alt={selectedEvent.event_type}
                sx={{ width: '100%', maxHeight: 400, objectFit: 'cover', mb: 2, cursor: 'pointer' }}
              />

              <TextField
                label="Event ID"
                fullWidth
                margin="dense"
                value={selectedEvent.id.toLocaleString()}
                slotProps={{ input: { readOnly: true } }}
              />

              <TextField
                label="Timestamp"
                fullWidth
                margin="dense"
                value={moment(selectedEvent.timestamp).format('dddd, MMMM Do YYYY, HH:mm:ss')}
                slotProps={{ input: { readOnly: true } }}
              />

              <TextField
                label="Vehicle ID"
                fullWidth
                margin="dense"
                value={selectedEvent.vehicle_identification}
                slotProps={{ input: { readOnly: true } }}
              />

              <Grid display={'flex'} gap={2}>
                <TextField
                  label="EAR"
                  fullWidth
                  margin="dense"
                  value={selectedEvent.ear.toFixed(2)}
                  slotProps={{ input: { readOnly: true } }}
                />

                <TextField
                  label="MAR"
                  fullWidth
                  margin="dense"
                  value={selectedEvent.mar.toFixed(2)}
                  slotProps={{ input: { readOnly: true } }}
                />
              </Grid>
            </DialogContent>

            <DialogActions sx={{ paddingBottom: 2 }}>
              <Button
                variant="outlined"
                color="secondary"
                onClick={handleDownload}
                sx={{
                  '&:hover': {
                    backgroundColor: (theme) => theme.palette.secondary.main,
                    color: (theme) => theme.palette.secondary.contrastText,
                    borderColor: (theme) => theme.palette.secondary.main,
                  },
                }}
              >
                Download
              </Button>
              <Button variant="contained" color="primary" onClick={handleDialogClose}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Snackbar feedback */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default EventGalleryPage;