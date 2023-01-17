CREATE_PREDICTIONS_TABLE = """\
CREATE TABLE IF NOT EXISTS predictions (
    prediction_for_date DATE NOT NULL,       -- Date for which prediction is made
    date_of_prediction  DATE NOT NULL,       -- Date prediction was made
    model_version       VARCHAR NOT NULL,    -- Version of model used to make prediction; date-like (e.g., "2022-12-31")
    energy_production   DOUBLE NOT NULL,     -- Energy production prediction (Wh)
    accuracy            DOUBLE DEFAULT NULL, -- TBD
    PRIMARY KEY (prediction_for_date, date_of_prediction, model_version)
);
"""
