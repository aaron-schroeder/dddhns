from typing import List

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from specialsauce.sources import trainingpeaks

from dddhns.domain.model import ActivityData
# from dddf.infrastructure.persistence.repository import ActivityDataRepository
from dddhns.ports.repository import AbstractExtractRepository


def activity_data(
    repository: AbstractExtractRepository
) -> List[ActivityData]:
    
    return repository.find_all()


def timeseries(
    repository: AbstractExtractRepository,
    activity_id: int,
) -> pd.DataFrame:
    if (
        (activity_data := repository.get(activity_id)) is None
        or (res := activity_data.get_timeseries()) is None
    ):
        return pd.DataFrame([])
    return res


def ngp_speed(
    repository: AbstractExtractRepository,
    activity_id: int,
) -> pd.DataFrame:
    if (
        (activity_data := repository.get(activity_id)) is None
        or (ts_df := activity_data.get_timeseries()) is None
    ):
        return None
    
    ngp_speed_series = ts_df['velocity_smooth']  \
                     * trainingpeaks.ngp_speed_factor(ts_df['grade_smooth']/100)
    elapsed_time_series = ts_df.index.to_series() - ts_df.index[0]
    elapsed_time_sec_series = elapsed_time_series.dt.total_seconds()

    elapsed_time_sec_scalar = elapsed_time_sec_series.iloc[-1]

    interp_fn = interp1d(elapsed_time_sec_series, ngp_speed_series,
                         kind='linear')
    elapsed_time_sec_series_1sec = np.arange(elapsed_time_sec_scalar + 1)
    ngp_speed_series_1sec = pd.Series(interp_fn(elapsed_time_sec_series_1sec))
    
    res = trainingpeaks.normalize(ngp_speed_series_1sec)

    return res


def pmc_fields(
    repository: AbstractExtractRepository
) -> pd.DataFrame:
    records = []
    for activity_data in repository.find_all():
        ts_df = activity_data.get_timeseries()
        if ts_df is not None:
            start_date = _get_start_date(ts_df)
            tss = _calculate_tss(ts_df)
            records.append({'recorded': start_date,
                            'type': activity_data.type,
                            'TSS': tss})
    return pd.DataFrame.from_records(records)


def _get_start_date(ts_df: pd.DataFrame):
    start_timestamp = ts_df.index[0].tz_convert('US/Arizona')
    return start_timestamp.date()


def _calculate_tss(ts_df: pd.DataFrame) -> float:
    ngp_speed_series = ts_df['velocity_smooth']  \
                     * trainingpeaks.ngp_speed_factor(ts_df['grade_smooth']/100)
    elapsed_time_series = ts_df.index.to_series() - ts_df.index[0]
    elapsed_time_sec_series = elapsed_time_series.dt.total_seconds()

    elapsed_time_sec_scalar = elapsed_time_sec_series.iloc[-1]

    interp_fn = interp1d(elapsed_time_sec_series, ngp_speed_series,
                         kind='linear')
    elapsed_time_sec_series_1sec = np.arange(elapsed_time_sec_scalar + 1)
    ngp_speed_series_1sec = pd.Series(interp_fn(elapsed_time_sec_series_1sec))
    
    ngp_speed_scalar = trainingpeaks.normalize(ngp_speed_series_1sec)
    
    ftp = 4.13  # m/s for 6:30/mile
    
    return trainingpeaks.training_stress_score(ngp_speed_scalar, ftp, 
                                               elapsed_time_sec_scalar)
        