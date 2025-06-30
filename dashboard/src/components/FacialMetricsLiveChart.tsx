import React, { useEffect, useRef, useState } from "react";
import { Box, Paper, Typography } from "@mui/material";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Legend,
  Tooltip
} from "chart.js";
import type { ChartOptions } from "chart.js"; 
import { HOST, PORT } from "../constant/urlConstant";

// Register ChartJS components
ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Legend, Tooltip);

interface FacialMetrics {
  ear: number;
  mar: number;
  is_drowsy: boolean;
  is_yawning: boolean;
}

const MAX_DATA_POINTS = 50;

const FacialMetricsChart: React.FC = () => {
  const [dataPoints, setDataPoints] = useState<
    { ear: number; mar: number; timestamp: string }[]
  >([]);

  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(`ws://${HOST}:${PORT}/realtime/data/facialmetrics`);


    ws.current.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.current.onmessage = (event) => {
      try {
        const parsed : FacialMetrics = JSON.parse(event.data);

        const newPoint = {
          ear: parsed.ear,
          mar: parsed.mar,
          timestamp: new Date().toLocaleTimeString(),
        };

        setDataPoints((prev) => {
          const updated = [...prev, newPoint];
          if (updated.length > MAX_DATA_POINTS) {
            updated.shift();
          }
          return updated;
        });
      } catch (err) {
        console.error("Error parsing websocket data:", err);
      }
    };

    ws.current.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    ws.current.onclose = () => {
      console.log("WebSocket disconnected");
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  const chartData = {
    labels: dataPoints.map((point) => point.timestamp),
    datasets: [
      {
        label: "EAR",
        data: dataPoints.map((point) => point.ear),
        borderColor: "rgba(75,192,192,1)",
        backgroundColor: "rgba(75,192,192,0.2)",
        fill: true,
        tension: 0.3,
      },
      {
        label: "MAR",
        data: dataPoints.map((point) => point.mar),
        borderColor: "rgba(255,99,132,1)",
        backgroundColor: "rgba(255,99,132,0.2)",
        fill: true,
        tension: 0.3,
      },
    ],
  };

  // Explicitly type options and use `animation: false` as literal
  const chartOptions: ChartOptions<"line"> = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    layout: {
      padding: {
        top: 10,
        bottom: 10,
        left: 15,
        right: 15,
      },
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          pointStyle: 'circle',
          boxWidth: 10,
          font: {
            size: 12,
          },
          padding: 15,
        },
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 0,
          autoSkip: true,
          maxTicksLimit: 10,
        },
      },
      y: {
        beginAtZero: true,
        suggestedMax: 1,
        ticks: {
          stepSize: 0.1,
        },
      },
    },
  };

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Typography variant="h2" gutterBottom>
        Facial Metrics Graph
      </Typography>
      <Box sx={{ flexGrow: 1 , width : '100%', height: '30vh'}}>
          <Line data={chartData} options={chartOptions} />
      </Box>
    </Paper>
  );
};

export default FacialMetricsChart;
