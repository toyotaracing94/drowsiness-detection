import React, { useState, useEffect } from "react";
import { Button, Box, Typography, Paper, Chip } from "@mui/material";
import axios from "axios";  // Import axios
import { API_URL_LOCATION } from "../constant/urlConstant";

const DetectionControl: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Stopped");
  const [isSystemRunning, setIsSystemRunning] = useState(false);

  // Function to check if the system is already running
  const checkStatus = async () => {
    try {
      const response = await axios.get(`${API_URL_LOCATION}/detection/status`);
      if (response.data.data.is_alive_thread && response.data.data.is_running) {
        setIsSystemRunning(true);
        setIsRunning(true);
        setStatusMessage("Running");
      } else {
        setIsSystemRunning(false);
        setIsRunning(false);
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
        setIsRunning(true);
        setIsPaused(false);
        setStatusMessage("Running");
        setIsSystemRunning(true); 
      }
    } catch (error) {
      console.error("Failed to start detection:", error);
    }
  };

  const handlePause = async () => {
    try {
      const response = await axios.post(`${API_URL_LOCATION}/detection/pause`);
      if (response.data.data) {
        setIsRunning(false);
        setIsPaused(true);
        setStatusMessage("Paused");
      }
    } catch (error) {
      console.error("Failed to pause detection:", error);
    }
  };

  const handleResume = async () => {
    try {
      const response = await axios.post(`${API_URL_LOCATION}/detection/resume`);
      if (response.data.data) {
        setIsRunning(true);
        setIsPaused(false);
        setStatusMessage("Running");
      }
    } catch (error) {
      console.error("Failed to resume detection:", error);
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
            color={isRunning ? (isPaused ? "warning" : "info") : "error"}
            />
        </Box>

        {/* Control Buttons */}
        <Box sx={{ display: "flex", gap: 2 }}>
          {!isRunning && !isPaused && !isSystemRunning? (
            // If not running, show "Start Detection" button
            <Button
              variant="contained"
              color="primary"
              onClick={handleStart}
              sx={{ width: 150 }}
            >
              Start Detection
            </Button>
          ) : isPaused? (
            // If running but paused, show "Resume Detection"
            <Button
              variant="contained"
              color="info"
              onClick={handleResume}
              sx={{ width: 150 }}
            >
              Resume Detection
            </Button>
          ) : (
            <>
              <Button
                variant="contained"
                color="error"
                onClick={handlePause}
                sx={{ width: 150 }}
              >
                Pause Detection
              </Button>
            </>
          )}
        </Box>
      </Box>
    </Paper>
  );
};

export default DetectionControl;