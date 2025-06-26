import { Grid } from "@mui/material";
import React from "react";
import SystemConfiguration from "../components/SystemConfiguration";
import ModelConfiguration from "../components/ModelConfiguration";
import LiveFeed from "../components/LiveFeed";
import FacialMetricsChart from "../components/FacialMetricsLiveChart";
import RecentDetectionEvent from "../components/RecentDetectionEvent";
import { API_URL_LOCATION } from "../constant/urlConstant";

const DashboardPage : React.FC = () => {
    return (
        <Grid container spacing={2} margin={2}>
            <Grid size={{ xs: 12, lg : 3 }}>
                <Grid>
                    <SystemConfiguration/>
                </Grid>
                <Grid>
                    <ModelConfiguration/>
                </Grid>
            </Grid>
            <Grid size={{ xs: 12, lg: 9 }}>
                <Grid container spacing={2}>
                    <Grid size={{ xs: 12, md: 6 }}>
                        <LiveFeed
                            src={`${API_URL_LOCATION}/realtime/video/raw`}
                            title="Live Camera"
                        />
                    </Grid>
                    
                    <Grid size={{ xs: 12, md: 6 }}>
                        <LiveFeed
                            src={`${API_URL_LOCATION}/realtime/video/processed`}
                            title="Live Detection"
                        />
                    </Grid>

                    <Grid size={{ xs: 12, md: 7 }}>
                        <FacialMetricsChart/>
                    </Grid>

                    <Grid size={{ xs: 12, md: 5 }}>
                        <RecentDetectionEvent/>
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    )
}

export default DashboardPage