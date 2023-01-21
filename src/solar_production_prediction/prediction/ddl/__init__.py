TABLE_NAME = "predictions"

CREATE_PREDICTIONS_TABLE = f"""\
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    prediction_for_date DATE NOT NULL,       -- Date for which prediction is made
    date_of_prediction  DATE NOT NULL,       -- Date prediction was made
    model_version       VARCHAR NOT NULL,    -- Version of model used to make prediction; date-like (e.g., "2022-12-31")
    energy_production   DOUBLE NOT NULL,     -- Energy production prediction (Wh)
    accuracy            DOUBLE DEFAULT NULL, -- TBD
    PRIMARY KEY (prediction_for_date, date_of_prediction, model_version)
);
"""

SWAP_ACCURACY_FOR_ACTUAL_WATTAGE = f"""\
ALTER TABLE {TABLE_NAME} RENAME COLUMN accuracy TO actual_energy_production;
"""