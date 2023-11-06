from dataclasses import dataclass

@dataclass
class Config():
    app_server: str = "localhost"
    app_port: int = 8080
    db_server: str = "localhost"
    db_port: int = 27017
    db_collection: str = "LegoPlans"
    page_length: int = 50


@dataclass
class PlanMetadata:
    set_number: str
    url: str
    description: str
    date_added: str     # to address
    date_modified: str  # to address
    # more...

@dataclass
class PlanQueueItem:
    set_number: int
    download_enabled: bool = False
    download_complete: bool = False

@dataclass
class Plan:
    set_number: int
    data: bytearray | None = None

