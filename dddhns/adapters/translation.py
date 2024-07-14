import datetime
from typing import List, Dict

from dateutil.parser import isoparse
import pandas as pd

from dddhns.domain import language as lang
from dddhns.domain import model

from dddhns.ports.translation import AbstractActivityDataTranslator


class StravaAPIActivityDataTranslator(AbstractActivityDataTranslator):
    # def to_activity_data(
    #     self,
    #     stream_data: list,
    #     start_time: datetime.datetime  # ideally would be entire summary_data
    # ) -> model.ActivityData:
    #     timeseries = self._to_timeseries(stream_data, start_time)
    #     return model.ActivityData(timeseries)

    def to_activity_data(
        self,
        stream_data: List,
        summary_data: Dict,
    ) -> model.ActivityData:
        start_time = isoparse(summary_data['start_date'])
        timeseries = self._to_timeseries(stream_data, start_time)
        return model.ActivityData(summary_data['id'], 
                                  type=summary_data['type'],
                                  timeseries=timeseries)
    
    def _to_timeseries(
        self,
        data: list, 
        start_time: datetime.datetime
    ) -> model.Timeseries:
        if data is None or len(data) == 0:
            return None
        dataframe = pd.DataFrame({stream['type']: stream['data']
                                  for stream in data})

        dataframe[lang.TIMESTAMP] = start_time  \
                                      + pd.to_timedelta(dataframe[lang.TIME], 
                                                        unit='s')
        dataframe = dataframe.set_index(lang.TIMESTAMP)

        if 'latlng' in dataframe.columns:
            dataframe[[lang.LAT, lang.LON]] = [(val[0], val[1])
                                               for val in dataframe['latlng']]

        available_variables = set(lang.VARIABLES) & set(dataframe.columns)
        dataframe = dataframe[list(available_variables)]
        
        return model.Timeseries(dataframe)