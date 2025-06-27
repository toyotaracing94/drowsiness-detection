import React from 'react';
import { Box, Button, Typography } from '@mui/material';

const NotFoundPage: React.FC = () => {
  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" color="error">
        404 - Page Not Found
      </Typography>
      <Typography variant="body1">
        Please have some water. The page you’re looking for doesn’t exist.
      </Typography>
      <Button href={"/"} variant='contained' sx={{marginTop:1}}>Go Back Home</Button>
    </Box>
  );
};

export default NotFoundPage;