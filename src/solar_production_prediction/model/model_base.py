import json
import typing

from sklearn.linear_model._base import LinearModel


class Model:
    _estimator: LinearModel
    _fieldnames: list[str]
    _kwargs: dict[str, typing.Any]
    _random_state: int
    _test_size: float
    _version: str

    def __init__(
        self,
        estimator: LinearModel,
        fieldnames: list[str],
        random_state: int,
        test_size: float,
        version: str,
        /,
        **kwargs: dict[str, typing.Any],
    ) -> None:
        self._estimator = estimator
        self._fieldnames = fieldnames
        self._random_state = random_state
        self._test_size = test_size
        self._version = version
        self._kwargs = kwargs

    @property
    def fieldnames(self) -> list[str]:
        return self._fieldnames

    @property
    def estimator(self) -> LinearModel:
        return self._estimator

    @property
    def random_state(self) -> int:
        """random state used in train_test_split."""
        return self._random_state

    @property
    def test_size(self) -> float:
        """percent (0..1) of data reserved for model testing"""
        return self._test_size

    @property
    def version(self) -> str:
        return self._version

    def to_json(self) -> str:
        return json.dumps(
            {
                "estimator": type(self._estimator).__name__,
                "fieldnames": self._fieldnames,
                "random_state": self._random_state,
                "test_size": self._test_size,
                "version": self._version,
                **self._kwargs,
            },
            indent=4,
        )
