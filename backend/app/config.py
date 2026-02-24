from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    opensearch_host: str = "localhost"
    opensearch_port: int = 9200
    opensearch_username: str = ""
    opensearch_password: str = ""
    opensearch_use_ssl: bool = False
    opensearch_index: str = "history_exam_bbox"

    # Absolute path to the directory that contains question images.
    # The image_path stored in OpenSearch is relative to this root.
    images_root: str = "/home/skrdlf/Desktop/llm/korea_history/korea_history"


settings = Settings()
