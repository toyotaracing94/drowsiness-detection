import { Grid } from "@mui/material";
import React from "react";
import SystemConfiguration from "../components/SystemConfiguration";
import ModelConfiguration from "../components/ModelConfiguration";
import LiveFeed from "../components/LiveFeed";
import FacialMetricsChart from "../components/FacialMetricsLiveChart";
import RecentDetectionEvent from "../components/RecentDetectionEvent";

const DashboardPage : React.FC = () => {
    return (
        <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 3 }}>
                <Grid>
                    <SystemConfiguration/>
                </Grid>
                <Grid>
                    <ModelConfiguration/>
                </Grid>
            </Grid>
            <Grid size={{ xs: 12, md: 9 }}>
                <Grid container spacing={2}>
                    <Grid size={{ xs: 12, md: 6 }}>
                        <LiveFeed
                            src="http://localhost:8000/realtime/video/raw"
                            title="Live Camera"
                        />
                    </Grid>
                    
                    <Grid size={{ xs: 12, md: 6 }}>
                        <LiveFeed
                            src="http://localhost:8000/realtime/video/processed"
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