import { createFileRoute } from "@tanstack/react-router";
import AqiPredictor from "@/components/AqiPredictor.jsx";

export const Route = createFileRoute("/")({
  component: AqiPredictor,
  head: () => ({
    meta: [
      {
        title: "AirSense — AI Air Quality Index Predictor",
      },
      {
        name: "description",
        content:
          "Enter pollutant values (PM2.5, PM10, NO2, SO2, CO, O3) and instantly see your predicted AQI with health insights.",
      },
    ],
  }),
});