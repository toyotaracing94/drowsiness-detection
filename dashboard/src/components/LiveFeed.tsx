import React, { useState, useEffect } from "react";
import { Paper, Typography } from "@mui/material";

interface LiveFeedProps {
  src: string;
  title?: string;
  fallbackSrc?: string;
  checkIntervalMs?: number;
}

const LiveFeed: React.FC<LiveFeedProps> = ({
  src,
  title = "Live Camera Feed",
  fallbackSrc = "/no-image-available.jpg",
  checkIntervalMs = 5000,
}) => {
  const [imgSrc, setImgSrc] = useState(src);
  const [hasError, setHasError] = useState(false);

  // Function to handle error on image load
  const handleImageError = () => {
    setHasError(true);
    setImgSrc(fallbackSrc);
  };

  useEffect(() => {
    if (!hasError) return;

    const interval = setInterval(() => {
      const testImg = new Image();
      testImg.src = src + "?timestamp=" + new Date().getTime();
      testImg.onload = () => {
        // Only update if the image is currently showing the fallback
        setHasError(false);

        setImgSrc((currentSrc) => {
          // Only change if we're currently showing the fallback
          if (currentSrc === fallbackSrc) {
            return src;
          }
          return currentSrc;
        });
      };
    }, checkIntervalMs);

    return () => clearInterval(interval);
  }, [hasError, src, fallbackSrc, checkIntervalMs]);

  return (
    <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
      <Typography variant="h2" gutterBottom>
        {title}
      </Typography>

      <img
        src={imgSrc}
        alt={title}
        onError={handleImageError}
        style={{
          maxHeight: "400px",
          borderRadius: 8,
          border: "1px solid #ddd",
          width: "100%",
          objectFit: "fill",
        }}
      />
    </Paper>
  );
};

export default LiveFeed;