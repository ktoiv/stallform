from app.service.data_builder_service import build_data_from_date
from datetime import date

start_date = date(2019, 7, 1)
build_data_from_date(start_date)