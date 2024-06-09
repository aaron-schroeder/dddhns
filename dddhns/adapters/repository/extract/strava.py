import abc
import datetime
import json
import os
from typing import List

from dateutil.parser import isoparse
import jsonschema
import pandas as pd

from dddhns.adapters import translation
from dddhns.domain import language as lang
from dddhns.domain.model import ActivityData, Timeseries
from dddhns.ports.repository import AbstractExtractRepository


class StravaJSONDirectoryExtractRepository(AbstractExtractRepository):
    def __init__(self, directory):
        # the top-level directory that contains all subdirs and files
        # The expected structure is :
        # - activities/
        #     - ${activity_id_1}/
        #         - summary.json
        #         - streams.json
        #     - ${activity_id_2}/
        #     ...
        self.directory = directory

    def get(self, activity_data_id):
        summary_data = self._load_summary_data(activity_data_id)
        streams_data = self._load_streams_data(activity_data_id)
        if summary_data is None or streams_data is None:
            return None
        translator = translation.StravaAPIActivityDataTranslator()
        return translator.to_activity_data(streams_data, summary_data)

    def find_all(self):
        activity_dir_path = os.path.join(self.directory, 'activities/')
        activity_ids = [int(f.name) for f in os.scandir(activity_dir_path) 
                        if f.is_dir()]
        res = []
        for activity_id in activity_ids:
            activity_data = self.get(activity_id)
            if activity_data is not None:
                res.append(activity_data)
        return res

    def _load_streams_data(self, activity_data_id):
        data_path = os.path.join(self.directory,
                                 f'activities/{activity_data_id}/streams.json')
        if not os.path.exists(data_path):
            return
        with open(data_path, 'r') as file:
            data = json.load(file)
        return data
    
    def _load_summary_data(self, activity_data_id):
        data_path = os.path.join(self.directory,
                                 f'activities/{activity_data_id}/summary.json')
        if not os.path.exists(data_path):
            return
        with open(data_path, 'r') as file:
            data = json.load(file)
        return data
    
    def _load_all_summary_data(self):
        data_path = os.path.join(self.directory, 'activities.jl')
        with open(data_path, 'r') as file:
            res = [json.loads(line) for line in file]
        return res


class StravaJSONFileExtractRepository(AbstractExtractRepository):
    def __init__(self, directory):
        self.directory = directory

    def find_all(self) -> List[ActivityData]:
        activity_summary_list = self._load_all_summary_data()
        res = []
        for activity_summary in activity_summary_list:
            # activity_data = ActivityDataFactory.create(
            #     index_type='timedelta', ...)
            # activity_data = ActivityData(
            #     summary=activity_summary, 
            #     timeseries=self._load_timeseries(activity_summary['id'])
            # )
            activity_data = self.get(activity_summary['id'])
            res.append(activity_data)
        return res

    def get(self, activity_data_id):
        summary_data = self._load_summary_data(activity_data_id)
        streams_data = self._load_streams_data(activity_data_id)
        translator = translation.StravaAPIActivityDataTranslator()

        return translator.to_activity_data(streams_data, summary_data)

        # timeseries_df = self._load_dataframe(activity_data_id)
        # if timeseries_df is not None:
        #     timeseries = Timeseries(timeseries_df) 
        # else:
        #     timeseries = None

        # if timeseries_df is None:
        #     timeseries = None
        # elif len(errors := Timeseries.get_validation_errors(timeseries_df)):
        #     delim = '\n    * '
        #     raise ValueError('Validation error(s): ' + delim + delim.join(errors))
        # else:
        #     # timeseries.index = timeseries.index.to_series().dt. ... some such
        #     timeseries = Timeseries(timeseries_df)

        # # timeseries = self._load_timeseries(activity_data_id)
        # return ActivityData(summary=summary_data, 
        #                     timeseries=timeseries)

    def _load_dataframe(self, activity_data_id):
        streams_data = self._load_streams_data(activity_data_id)
        if streams_data is None:
            return
        
        print(streams_data)

        # summary_data = self._load_summary_data(activity_data_id)
        # start_time = isoparse(summary_data['start_date'])

        # return translation.from_strava_streams_data(streams_data)
        data = pd.DataFrame({stream['type']: stream['data'] 
                             for stream in streams_data}
        ) # .set_index(dialect.TIME)
        
        if 'latlng' in data.columns:
            data[[lang.LAT, lang.LON]] = [
                (val[0], val[1])for val in data['latlng']
            ]

        # available_variables = list(set(lang.VARIABLES) & set(data.columns))

        return data
        # return data[available_variables]

    def _load_streams_data(self, activity_data_id):
        data_path = os.path.join(self.directory, 
                                 f'streams/{activity_data_id}.json')
        if not os.path.exists(data_path):
            return
        with open(data_path, 'r') as file:
            data = json.load(file)
        streams_data = self._validate_streams_data(data['data'])
        return streams_data
    
    def _load_summary_data(self, activity_data_id):
        data_path = os.path.join(self.directory, 'activities.jl')
        with open(data_path, 'r') as file:
            for line in file:
                activity_summary_data = json.loads(line)
                if activity_summary_data.get('id', 0) == activity_data_id:
                    return activity_summary_data
                
    def _load_all_summary_data(self):
        data_path = os.path.join(self.directory, 'activities.jl')
        with open(data_path, 'r') as file:
            res = [json.loads(line) for line in file]
        return res

    def _validate_streams_data(self, data):
        schema = {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['type', 'data'],
                'properties': {'data': {'type': 'array'}},
            },
        }
        jsonschema.validate(instance=data, schema=schema)
        return data

