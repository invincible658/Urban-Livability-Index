CREATE TABLE livability_data (
    area_id INT,
    area_name TEXT,
    price_per_sqft FLOAT,
    congestion_score FLOAT,
    aqi FLOAT,
    growth_score FLOAT,
    final_score FLOAT,
    rank FLOAT
);

SELECT * FROM livability_data;