-- Tables for the who-paid-the-tariff project. 

DROP TABLE IF EXISTS prices;
DROP TABLE IF EXISTS product_tariff_crosswalk;
-- One row per product - whether it was hit by the March 2025 counter-tariffs
CREATE TABLE product_tariff_crosswalk (
    product  TEXT PRIMARY KEY,   -- product name, unique
    status   TEXT NOT NULL,      -- 'tariffed' or 'not tariffed'
    hs_code  TEXT                -- HS code (first 6 digits); blank if not tariffed
);

-- One row per product, place and month
CREATE TABLE prices (
    date DATE NOT NULL,
    place TEXT NOT NULL,
    product TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (date, place, product),
    FOREIGN KEY (product) REFERENCES product_tariff_crosswalk (product)
);