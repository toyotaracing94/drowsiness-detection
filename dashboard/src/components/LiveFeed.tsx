import React, { useState, useEffect } from "react";
import { Paper, Typography } from "@mui/material";

interface LiveFeedProps {
  src: string;
  title?: string;
  fallbackSrc?: string;
  checkIntervalMs?: number; // how often to retry, default 5000ms
}

const LiveFeed: React.FC<LiveFeedProps> = ({
  src,
  title = "Live Camera Feed",
  fallbackSrc = "/images/no-stream.png",
  checkIntervalMs = 5000,
}) => {
  const [imgSrc, setImgSrc] = useState(src);
  const [hasError, setHasError] = useState(false);

  // Function to handle error on image load
  const handleImageError = () => {
    setHasError(true);
    setImgSrc(fallbackSrc);
  };

  // Function to handle successful image load
  const handleImageLoad = () => {
    setHasError(false);
    setImgSrc(src);
  };

  useEffect(() => {
    if (hasError) {
      // When error state is true, try to reload the original src every checkIntervalMs milliseconds
      const interval = setInterval(() => {
        // Create a new Image object to test if src is reachable
        const testImg = new Image();
        testImg.src = src + "?timestamp=" + new Date().getTime();
        testImg.onload = () => {
          setHasError(false);
          setImgSrc(src);
        };
        testImg.onerror = () => {
          // still error, keep fallback
        };
      }, checkIntervalMs);

      return () => clearInterval(interval);
    }
  }, [hasError, src, checkIntervalMs, fallbackSrc]);

  return (
    <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>

      <img
        src={imgSrc}
        alt={title}
        onError={handleImageError}
        onLoad={handleImageLoad}
        style={{
          maxHeight: "400px",
          borderRadius: 8,
          border: "1px solid #ddd",
          width: "100%",
          objectFit: "contain",
        }}
      />
    </Paper>
  );
};

export default LiveFeed;