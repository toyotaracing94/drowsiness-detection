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
import { API_URL_LOCATION, HOST, PORT } from "../constant/urlConstant";

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
    const ws = new WebSocket(`ws://${HOST}:${PORT}/realtime/notification/drowsiness`);

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = async (event) => {
      const eventId = JSON.parse(event.data);
      try {
        const res = await fetch(`${API_URL_LOCATION}/drowsinessevent/${eventId}`);
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
      <Typography variant="h2" fontWeight={600} gutterBottom>
        Detection Log
      </Typography>

      <List dense>
        {logs.map((log, index) => (
          <Box key={log.id}>
            <ListItem>
              <Avatar
                variant="rounded"
                src={log.image}
                alt="Detection"
                sx={{ width: 56, height: 56, mr: 2 }}
              />
              <ListItemText
                primary={
                  <Box sx={{display: "flex", flexWrap: "wrap", gap: 1 }}>
                    <Chip
                      label={log.event_type}
                      color="warning"
                      size="small"
                    />
                    <Typography variant="body2">
                      {new Date(log.timestamp).toLocaleString(undefined, {
                        dateStyle: "medium",
                        timeStyle: "medium",
                      })}
                    </Typography>
                  </Box>
                }
                secondary={
                  <>
                    <Typography variant="body2" component="span" sx={{ fontStyle: 'italic' }}>
                      <strong>Event ID:</strong> {log.id}
                    </Typography>
                    <br />
                    <Typography variant="body2" component="span">
                      <strong>Vehicle:</strong> {log.vehicle_identification}
                    </Typography>
                    <br />
                    <Typography variant="caption" component="span">
                      <strong>EAR:</strong> {log.ear.toFixed(2)} | <strong>MAR:</strong> {log.mar.toFixed(2)}
                    </Typography>
                  </>
                }
              />
            </ListItem>
            {index < logs.length - 1 && <Divider variant="inset" component="li" />}
          </Box>
        ))}
      </List>
    </Paper>
  );
};

export default RecentDetectionEvent;