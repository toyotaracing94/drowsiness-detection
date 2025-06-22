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
            <Grid size={3}>
                <SystemConfiguration/>
                <ModelConfiguration/>
            </Grid>
            <Grid container size={9} spacing={2}>
                <Grid container size={12}>
                    <Grid size={6}>
                        <LiveFeed
                        src="http://localhost:8000/realtime/video/raw"
                        title="Live Camera Feed"
                        />
                    </Grid>
                    
                    <Grid size={6}>
                        <LiveFeed
                        src="http://localhost:8000/realtime/video/processed"
                        title="Live Drowsiness Detection Feed"
                    />
                    </Grid>
                </Grid>
                <Grid size={9}>
                    <FacialMetricsChart></FacialMetricsChart>
                </Grid>
                <Grid size={3}>
                    <RecentDetectionEvent></RecentDetectionEvent>
                </Grid>
            </Grid>
        </Grid>
    )
}

export default DashboardPage