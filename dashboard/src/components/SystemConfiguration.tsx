import React, { useState } from "react";
import {
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Paper,
} from "@mui/material";

const SystemConfiguration: React.FC = () => {
  const [camera, setCamera] = useState("dev/video0");
  const [earThreshold, setEarThreshold] = useState(0.25);
  const [marThreshold, setMarThreshold] = useState(0.6);
  const [drowsyDuration, setDrowsyDuration] = useState(2);

  return (
    <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        System Configuration
      </Typography>

      <FormControl fullWidth margin="normal">
        <InputLabel>Camera Source</InputLabel>
        <Select
          value={camera}
          onChange={(e) => setCamera(e.target.value)}
        >
          <MenuItem value="dev/video0">dev/video0</MenuItem>
          <MenuItem value="dev/video1">dev/video1</MenuItem>
        </Select>
      </FormControl>

      <Typography gutterBottom>
        Eye Closure Threshold (EAR): {earThreshold.toFixed(2)}
      </Typography>
      <Slider
        value={earThreshold}
        onChange={(_, value) => setEarThreshold(value as number)}
        step={0.01}
        min={0.1}
        max={0.5}
      />

      <Typography gutterBottom>
        Mouth Opening Threshold (MAR): {marThreshold.toFixed(2)}
      </Typography>
      <Slider
        value={marThreshold}
        onChange={(_, value) => setMarThreshold(value as number)}
        step={0.01}
        min={0.1}
        max={1}
      />

      <Typography gutterBottom>
        Drowsy Duration (seconds): {drowsyDuration}
      </Typography>
      <Slider
        value={drowsyDuration}
        onChange={(_, value) => setDrowsyDuration(value as number)}
        step={0.5}
        min={1}
        max={5}
      />
    </Paper>
  );
};

export default SystemConfiguration;