import os

SIM_API   = os.getenv("SIM_API",   "http://localhost:8080/api")
STORE_API = os.getenv("STORE_API", "http://localhost:8082/api")
SELF_HOST = os.getenv("SELF_HOST", "http://localhost:7000")

DELTA_PC  = 10.0
PERIOD_S  = 900
DT_S      = 60
