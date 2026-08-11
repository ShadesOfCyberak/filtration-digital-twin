// InfluxDB Downsampling Task
// Downsamples raw sensor metrics into 5-minute averages every 5 minutes

option task = {
  name: "downsample_5m",
  every: 5m,
}

from(bucket: "filtration_bucket")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "sensor_data")
  |> aggregateWindow(every: 5m, fn: mean)
  |> to(bucket: "filtration_downsampled_1h", org: "filtration_org")
