import React from "react";
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
} from "@mui/material";

const dummyLogs = [
  { time: "10:22:01", status: "Drowsy" },
  { time: "10:21:43", status: "Normal" },
  { time: "10:21:30", status: "Drowsy" },
];

const RecentDetectionEvent: React.FC = () => {
  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Detection Log
      </Typography>
      <List dense>
        {dummyLogs.map((log, index) => (
          <React.Fragment key={index}>
            <ListItem>
              <ListItemText primary={log.status} secondary={log.time} />
            </ListItem>
            {index < dummyLogs.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default RecentDetectionEvent;