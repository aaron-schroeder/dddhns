import abc
import datetime

import pandas as pd

from dddhns.domain import language as lang


class AbstractActivityDataTranslator(abc.ABC):
    @abc.abstractmethod
    def to_activity_data(self, *args, **kwargs):
        raise NotImplementedError
