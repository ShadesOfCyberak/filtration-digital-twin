from typing import List, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    url: str = Field(default="http://localhost:8086", alias="INFLUXDB_URL")
    token: str = Field(default="my-super-secret-influxdb-admin-token", alias="INFLUXDB_TOKEN")
    org: str = Field(default="filtration_org", alias="INFLUXDB_ORG")
    bucket: str = Field(default="filtration_bucket", alias="INFLUXDB_BUCKET")


class MQTTSettings(BaseSettings):
    broker_host: str = Field(default="localhost", alias="MQTT_BROKER_HOST")
    broker_port: int = Field(default=1883, alias="MQTT_BROKER_PORT")
    client_id: str = Field(default="digital_twin_backend", alias="MQTT_CLIENT_ID")
    topic_prefix: str = Field(default="filtration", alias="MQTT_TOPIC_PREFIX")
    qos: int = 1
    keep_alive: int = 60


class SecuritySettings(BaseSettings):
    jwt_secret_key: str = Field(default="super-secret-jwt-signing-key-for-digital-twin-32-chars", alias="JWT_SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


class APISettings(BaseSettings):
    title: str = "Filtration System Digital Twin API"
    description: str = "IoT-enabled digital twin for machine health monitoring and failure prediction"
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    cors_origins: Union[List[str], str] = ["*"]


class LoggingSettings(BaseSettings):
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = "json"


class DigitalTwinSettings(BaseSettings):
    filter_area: float = 0.05  # m^2
    filter_thickness: float = 0.01  # m
    medium_resistance_clean: float = 1e10  # m^-1
    max_cake_resistance: float = 5e11  # m^-1
    fouling_rate_constant: float = 0.001
    pump_a: float = 5.0  # bar
    pump_b: float = 0.0005  # bar / (L/min)^2
    pump_efficiency: float = 0.75
    fluid_viscosity: float = 0.001  # Pa*s
    
    # Thresholds
    warning_residual_threshold: float = 0.25  # 25% deviation
    critical_residual_threshold: float = 0.50  # 50% deviation
    backwash_clogging_index_threshold: float = 200.0


class Settings(BaseSettings):
    environment: str = Field(default="development", alias="ENVIRONMENT")
    db: DatabaseSettings = DatabaseSettings()
    mqtt: MQTTSettings = MQTTSettings()
    security: SecuritySettings = SecuritySettings()
    api: APISettings = APISettings()
    logging: LoggingSettings = LoggingSettings()
    twin: DigitalTwinSettings = DigitalTwinSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
