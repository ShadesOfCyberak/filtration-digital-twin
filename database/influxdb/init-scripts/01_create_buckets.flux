// InfluxDB 2.x Bucket Initialization Script
// Create raw telemetry, health metrics, and digital twin state buckets

import "influxdata/influxdb/v1"

// Raw Telemetry Bucket (30 day retention)
v1.createBucket(
    name: "filtration_bucket",
    org: "filtration_org",
    retention: 30d
)

// Downsampled Aggregates Bucket (1 year retention)
v1.createBucket(
    name: "filtration_downsampled_1h",
    org: "filtration_org",
    retention: 365d
)
