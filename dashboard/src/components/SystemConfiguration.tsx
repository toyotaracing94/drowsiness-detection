import React, { useState } from "react";
import {
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Paper,
  Box,
} from "@mui/material";

const SystemConfiguration: React.FC = () => {
  const [camera, setCamera] = useState("dev/video0");
  const [earThreshold, setEarThreshold] = useState(0.25);
  const [marThreshold, setMarThreshold] = useState(0.6);
  const [drowsyDuration, setDrowsyDuration] = useState(2);

  return (
    <Paper variant="outlined" sx={{ p: 3, mb: 2 }}>
      <Typography variant="h2" gutterBottom>
        System Configuration
      </Typography>

      <FormControl fullWidth margin="normal">
        <InputLabel>Camera Source</InputLabel>
        <Select value={camera} onChange={(e) => setCamera(e.target.value)}>
          <MenuItem value="dev/video0">dev/video0</MenuItem>
          <MenuItem value="dev/video1">dev/video1</MenuItem>
        </Select>
      </FormControl>

      <Box sx={{ my: 1 }}>
        <Typography sx={styles.label}>
          Eye Closure Threshold (EAR):{" "}
          <span style={{ fontWeight: "bold" }}>
            {earThreshold.toFixed(2)}
          </span>
        </Typography>
        <Slider
          value={earThreshold}
          onChange={(_, value) => setEarThreshold(value as number)}
          step={0.01}
          min={0.1}
          max={0.5}
        />
      </Box>

      <Box sx={{ my: 1 }}>
        <Typography sx={styles.label}>
          Mouth Opening Threshold (MAR):{" "}
          
          <span style={{ fontWeight: "bold" }}>
            {marThreshold.toFixed(2)}
          </span>
        </Typography>
        <Slider
          value={marThreshold}
          onChange={(_, value) => setMarThreshold(value as number)}
          step={0.01}
          min={0.1}
          max={1}
        />
      </Box>

      <Box sx={{ my: 1 }}>
        <Typography sx={styles.label}>
          Drowsy Duration (seconds):{" "}
          <span style={{ fontWeight: "bold" }}>{drowsyDuration}</span>
        </Typography>
        <Slider
          value={drowsyDuration}
          onChange={(_, value) => setDrowsyDuration(value as number)}
          step={0.5}
          min={1}
          max={5}
        />
      </Box>
    </Paper>
  );
};

/** @type {import('@mui/material').SxProps} */
const styles = {
  label: {
    fontWeight: 500,
    mb: 1,
    fontSize: '0.9rem'
  }
};


export default SystemConfiguration;