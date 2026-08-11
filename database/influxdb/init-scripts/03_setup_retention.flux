// Retention Policy setup
// Ensure raw telemetry retained for 30 days
option task = {
  name: "enforce_retention_policies",
  every: 24h
}

// InfluxDB handles bucket retention natively via bucket configuration
