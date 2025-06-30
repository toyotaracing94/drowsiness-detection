import { createTheme } from "@mui/material";
import { green, grey } from "@mui/material/colors";

const theme = createTheme({
  palette: {
    primary : {
        main : grey[900]
    },
    secondary : {
        main : green[700]
    }
  },
  typography: {
    fontFamily: '"Montserrat", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 500,
      fontSize: '2.5rem',
      lineHeight: 1.2,
    },
    h2: {
      fontWeight: 800,
      fontSize: '1.2rem',
      lineHeight: 1.3,
    }
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 16px',
          textTransform: 'none',
        },
      },
    },
  },
});

export default theme;