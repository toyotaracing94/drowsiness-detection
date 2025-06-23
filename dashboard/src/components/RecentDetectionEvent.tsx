import React, { useEffect, useState } from "react";
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
  Avatar,
  Chip,
  Box,
} from "@mui/material";

interface DrowsinessEvent {
  timestamp: string;
  vehicle_identification: string;
  image: string;
  mar: number;
  ear: number;
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
      try {
        const res = await fetch(`http://localhost:8000/drowsinessevent/${eventId}`);
        if (!res.ok) {
          console.error("Failed to fetch event data", res.statusText);
          return;
        }
        const eventData: DrowsinessEvent = await res.json();

        setLogs((prev) => {
          if (prev.find((e) => e.id === eventData.id)) return prev;
          const updated = [eventData, ...prev];
          return updated.slice(0, 5);
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
            <ListItem alignItems="flex-start">
              <Avatar
                variant="rounded"
                src={log.image}
                alt="Detection"
                sx={{ width: 56, height: 56, mr: 2 }}
              />
              <ListItemText
                primary={
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Chip
                      label={log.event_type}
                      color={log.event_type.toLowerCase().includes("drowsy") ? "error" : "warning"}
                      size="small"
                    />
                    <Typography variant="body2" color="text.secondary">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </Typography>
                  </Box>
                }
                secondary={
                  <>
                    <Typography variant="body2" color="text.primary" component="span">
                      Vehicle: {log.vehicle_identification}
                    </Typography>
                    <br />
                    <Typography variant="body2" color="text.secondary" component="span" sx={{ fontStyle: 'italic' }}>
                      Event ID: {log.id}
                    </Typography>
                    <br />
                    <Typography variant="caption" color="text.secondary" component="span">
                      EAR: {log.ear.toFixed(2)} | MAR: {log.mar.toFixed(2)}
                    </Typography>
                  </>
                }
              />
            </ListItem>
            {index < logs.length - 1 && <Divider variant="inset" component="li" />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default RecentDetectionEvent;