import React, { useEffect, useState } from "react";
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
} from "@mui/material";

interface DrowsinessEvent {
  timestamp: string;
  vehicle_identificataion : string;
  image : string;
  mar : number;
  ear : number;
  id: string;
  event_type: string;
}

const RecentDetectionEvent: React.FC = () => {
  const [logs, setLogs] = useState<DrowsinessEvent[]>([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/realtime/notification/drowsiness");

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = async (event) => {
      const eventId = JSON.parse(event.data);
      console.log("Received event ID:", eventId);

      try {
        const res = await fetch(`http://localhost:8000/drowsinessevent/${eventId}`);
        if (!res.ok) {
          console.error("Failed to fetch event data", res.statusText);
          return;
        }
        const eventData: DrowsinessEvent = await res.json();

        setLogs((prev) => {
          // Avoid duplicates
          if (prev.find((e) => e.id === eventData.id)) return prev;
          return [eventData, ...prev]; // Append new event, no limit
        });
      } catch (error) {
        console.error("Error fetching event data:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Detection Log
      </Typography>
      <List dense>
        {logs.map((log, index) => (
          <React.Fragment key={log.id}>
            <ListItem>
              <ListItemText
                primary={log.event_type}
                secondary={new Date(log.timestamp).toLocaleTimeString()}
              />
            </ListItem>
            {index < logs.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default RecentDetectionEvent;