import React, { useState } from "react";
import {
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Paper,
} from "@mui/material";

const ModelConfiguration: React.FC = () => {
  const [camera, setCamera] = useState("dev/video0");
  const [maxPerson, setMaxPerson] = useState(2);
  const [modelType, setModelType] = useState("auto");

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Typography variant="h2" gutterBottom>
        Model Configuration
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

      <TextField
        label="Max Person"
        type="number"
        fullWidth
        margin="normal"
        value={maxPerson}
        onChange={(e) => setMaxPerson(Number(e.target.value))}
      />

      <FormControl fullWidth margin="normal">
        <InputLabel>Model</InputLabel>
        <Select
          value={modelType}
          onChange={(e) => setModelType(e.target.value)}
        >
          <MenuItem value="auto">Auto</MenuItem>
          <MenuItem value="fast">Fast</MenuItem>
          <MenuItem value="accurate">Accurate</MenuItem>
        </Select>
      </FormControl>
    </Paper>
  );
};

export default ModelConfiguration;