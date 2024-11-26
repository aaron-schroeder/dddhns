"""
Port classes. The interface half of the equation.    

Ref:
    https://www.cosmicpython.com/book/chapter_02_repository.html
    #what_is_a_port_and_what_is_an_adapter
"""
import abc
from dataclasses import dataclass
import os
from typing import List

import pandas as pd

from dddhns.domain.model import ActivityData


class AbstractExtractRepository(abc.ABC):
    @abc.abstractmethod
    def find_all(self) -> List[ActivityData]:
        """Retrieve every stored ActivityData entity."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def get(self, key: object) -> ActivityData:
        """Retrieve a stored ActivityData entity by key."""
        raise NotImplementedError

    # @abc.abstractmethod
    # def filter_by_column(self, column_name: str) -> pd.Series:
    #     # Return all data for the specified column name across all time series
    #     raise NotImplementedError

    # @abc.abstractmethod
    # def filter_by_date_range(self, start_time: datetime.date, 
    #                                end_time: datetime.date) -> pd.DataFrame:
    #     # Return data for all time series within the specified time range
    #     raise NotImplementedError


class AbstractExportRepository(abc.ABC):
    @abc.abstractmethod
    def save(self, activity_data: ActivityData) -> None:
        """Load the ActivityData objects into the repository"""
        raise NotImplementedError

    @abc.abstractmethod
    def save_all(self, *args: ActivityData) -> None:
        """Load the ActivityData objects into the repository"""
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, key) -> bool:
        raise NotImplementedError
