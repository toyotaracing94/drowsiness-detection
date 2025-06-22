import React from "react";
import { Paper, Typography } from "@mui/material";

const FacialMetricsChart: React.FC = () => {
  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        EAR / MAR Graph
      </Typography>
      {/* Placeholder */}
      <div style={{ height: 200, background: "#f5f5f5", borderRadius: 8 }} />
    </Paper>
  );
};

export default FacialMetricsChart;