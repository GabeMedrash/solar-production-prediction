import dataclasses

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import (
    train_test_split,
)

from .load import load_data

RANDOM_STATE = 6853


@dataclasses.dataclass
class Model:
    coefficient_of_determination: float
    fieldnames: list[str]  # exact ordering of data fields
    model: LinearRegression
    random_state: int  # random state used in train_test_split
    rmse_test: float
    rmse_train: float
    test_size: float  # percent (0..1) of data reserved for model testing


def train(test_size=0.25) -> Model:
    X, Y, fieldnames = load_data()
    x_train, x_test, y_train, y_test = train_test_split(
        X, Y, test_size=test_size, random_state=RANDOM_STATE
    )

    regression_model = LinearRegression()
    regression_model.fit(x_train, y_train)

    return Model(
        model=regression_model,
        coefficient_of_determination=regression_model.score(x_test, y_test),
        fieldnames=fieldnames,
        random_state=RANDOM_STATE,
        rmse_test=mean_squared_error(
            y_test, regression_model.predict(x_test), squared=False
        ),
        rmse_train=mean_squared_error(
            y_train, regression_model.predict(x_train), squared=False
        ),
        test_size=test_size,
    )
