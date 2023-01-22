from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import (
    train_test_split,
)

from ..model_base import Model

RANDOM_STATE = 6853
TEST_SIZE = 0.25
VERSION = "2022-12-30"


def train(
    X: list[list[float | int]], Y: list[float | int], fieldnames: list[str]
) -> Model:
    x_train, x_test, y_train, y_test = train_test_split(
        X, Y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    regression_model = LinearRegression()
    regression_model.fit(x_train, y_train)

    return Model(
        regression_model,
        fieldnames,
        RANDOM_STATE,
        TEST_SIZE,
        VERSION,
        coefficient_of_determination=regression_model.score(x_test, y_test),
        rmse_test=mean_squared_error(
            y_test, regression_model.predict(x_test), squared=False
        ),
        rmse_train=mean_squared_error(
            y_train, regression_model.predict(x_train), squared=False
        ),
    )
