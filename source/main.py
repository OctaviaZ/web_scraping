import pandas as pd
from selenium_scrapper_optimized import get_product_prices

data = get_product_prices()
df = pd.DataFrame.from_records(data)
df.to_csv("dataset/mercadona_price_data_spain_231113.csv", index=False,
    sep = ";")