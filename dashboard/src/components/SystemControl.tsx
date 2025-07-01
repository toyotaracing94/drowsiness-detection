import axios from "axios";
import React, { useState, useEffect } from "react";
import { Button, Box, Typography, Paper, Chip, Snackbar, Alert } from "@mui/material";
import { API_URL_LOCATION } from "../constant/urlConstant";

const DetectionControl: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [isSystemActive, setIsSystemActive] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Stopped");

  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'warning' | 'info',
  });
  const [loadingAction, setLoadingAction] = useState<string | null>(null);

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'warning' | 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  // Function to check if the system is already running
  const checkStatus = async () => {
    try {
      const response = await axios.get(`${API_URL_LOCATION}/detection/status`);
      // The thread is alive and the service is running, meaning it's running normally
      if (response.data.data.is_alive && response.data.data.is_running) {
        setIsSystemActive(true);
        setIsRunning(true);
        setStatusMessage("Running");
        return;
      }
      // The thread is alive but the service is not running, meaning it's paused
      if (response.data.data.is_alive && !response.data.data.is_running){
        setIsSystemActive(true);
        setIsRunning(false);
        setStatusMessage("Paused");
        return;
      }
      // The thread is not alive
      if(!response.data.data.is_alive){
        setIsSystemActive(false);
        setIsRunning(response.data.data.is_running)
        setStatusMessage("Stopped");
      }
    } catch (error) {
      console.error("Failed to fetch system status:", error);
    }
  };

  // Run the checkStatus when the component mounts
  useEffect(() => {
    checkStatus();
  }, []);

  // Button click handlers with API calls
  const handleStart = async () => {
    try {
      const response = await axios.post(`${API_URL_LOCATION}/detection/restart`);
      if (response.data.data) {
        setIsSystemActive(true); 
        setIsRunning(true);
        setStatusMessage("Running");
        showSnackbar("Detection started successfully.", "success");
      }
    } catch (error) {
      console.error("Failed to restart detection:", error);
      showSnackbar("Failed to start detection.", "error");
    }
  };

  const handlePause = async () => {
    try {
      const response = await axios.post(`${API_URL_LOCATION}/detection/pause`);
      if (response.data.data) {
        setIsSystemActive(true); 
        setIsRunning(false);
        setStatusMessage("Paused");
        showSnackbar("Detection paused.", "info");
      }
    } catch (error) {
      console.error("Failed to pause detection:", error);
      showSnackbar("Failed to pause detection.", "error");
    }
  };

  const handleResume = async () => {
    try {
      const response = await axios.post(`${API_URL_LOCATION}/detection/resume`);
      if (response.data.data) {
        setIsSystemActive(true); 
        setIsRunning(true);
        setStatusMessage("Resume");
        showSnackbar("Detection resumed.", "success");
      }
    } catch (error) {
      console.error("Failed to resume detection:", error);
      showSnackbar("Failed to resume detection.", "error");
    }
  };

  const handleStop = async () => {
    try {
      setLoadingAction('stop');
      const response = await axios.post(`${API_URL_LOCATION}/detection/stop`);
      if (response.data.data) {
        setIsSystemActive(false); 
        setIsRunning(false);
        setStatusMessage("Stop");
        showSnackbar("Detection stopped.", "info");
      }
    } catch (error) {
      console.error("Failed to stop detection:", error);
      showSnackbar("Failed to stop detection.", "error");
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <Paper variant="outlined" sx={{ p: 3, mb: 2 }}>
      <Typography variant="h2" gutterBottom>
        Drowsiness Detection Control
      </Typography>

      <Box sx={{display: 'flex', flexDirection: 'column', gap: 2, alignItems:'flex-start' }}>
        {/* Status Display */}
        <Box sx={{display:'flex', gap:1, alignItems: 'center'}}>
            <Typography>
                System :
            </Typography>
            <Chip
            label={statusMessage}
            color={isRunning ? "info" : "error"}
            />
        </Box>

        {/* Control Buttons */}
        <Box sx={{ display: "flex", gap: 2 }}>
          {(!isSystemActive && !isRunning) ? (
            // If thread is not active, show "Start Detection" button
            // But it doesn't really do much, as probably the backend doesn't even start
            <Button
              variant="contained"
              color="primary"
              onClick={handleStart}
              sx={{paddingX:'16px'}}
            >
              Start Detection
            </Button>
          ) : (isSystemActive && !isRunning) ? (
            // If the thread is still active but thread is not running the service
            // Then the service is on paused, show "Resume" button
            <Box display={'flex'} gap={1}>
              <Button
                variant="contained"
                color="info"
                onClick={handleResume}
                sx={{ paddingX:'16px'}}
              >
                Resume Detection
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={handleStop}
                loading={loadingAction === 'stop'}
                loadingPosition="end"
                sx={{ paddingX:'16px'}}
              >
                Stop Detection
              </Button>
            </Box>

          ) : (isSystemActive && isRunning) ? (
            // If the thread is still active but the thread is running the service
            // Pause this sucker
            <Button
              variant="contained"
              color="error"
              onClick={handlePause}
              sx={{ paddingX:'16px'}}
            >
              Pause Detection
            </Button>
          ): null}
        </Box>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={2000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
      
    </Paper>
  );
};

export default DetectionControl;