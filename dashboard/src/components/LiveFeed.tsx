import React, { useState, useEffect } from "react";
import { Box, Paper, Typography } from "@mui/material";

interface LiveFeedProps {
  src: string;
  title?: string;
  checkIntervalMs?: number;
}

const LiveFeed: React.FC<LiveFeedProps> = ({
  src,
  title = "Live Camera Feed",
  checkIntervalMs = 5000,
}) => {
  const [imgSrc, setImgSrc] = useState(`${src}?timestamp=${Date.now()}`);
  const [hasError, setHasError] = useState(false);

  const handleImageError = () => {
    setHasError(true);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setImgSrc(`${src}?timestamp=${Date.now()}`); // bust cache
    }, checkIntervalMs);

    return () => clearInterval(interval);
  }, [src, checkIntervalMs]);

  return (
    <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
      <Typography variant="h2" gutterBottom>
        {title}
      </Typography>

      <Box
        sx={{
          position: "relative",
          width: "100%",
          aspectRatio: "16 / 9",
          border: "1px solid #ddd",
          borderRadius: 1,
          overflow: "hidden",
          backgroundColor: hasError ? "black" : "transparent",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {hasError ? (
          <Typography
            variant="h6"
            sx={{
              color: "white",
              textAlign: "center",
            }}
          >
            Stream is not available
          </Typography>
        ) : (
          <img
            src={imgSrc}
            alt={title}
            onError={handleImageError}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "fill",
            }}
          />
        )}
      </Box>
    </Paper>
  );
};

export default LiveFeed;