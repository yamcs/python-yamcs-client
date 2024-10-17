import datetime
from typing import List, Optional

from yamcs.client.core.context import Context
from yamcs.client.core.helpers import to_server_time
from yamcs.client.tco.model import TCOStatus, TofInterval
from yamcs.protobuf.tco import tco_pb2

__all__ = [
    "TCOClient",
]


class TCOClient:
    """
    Client for interacting with a Time Correlation service managed by Yamcs.
    """

    def __init__(self, ctx: Context, instance: str, service: str):
        super(TCOClient, self).__init__()
        self.ctx = ctx
        self._instance = instance
        self._service = service

    def get_status(self) -> TCOStatus:
        """
        Retrieve the TCO status.
        """
        response = self.ctx.get_proto(f"/tco/{self._instance}/{self._service}/status")
        message = tco_pb2.TcoStatus()
        message.ParseFromString(response.content)
        return TCOStatus(message)

    def reconfigure(
        self,
        accuracy: Optional[float] = None,
        validity: Optional[float] = None,
        ob_delay: Optional[float] = None,
        default_tof: Optional[float] = None,
    ):
        """
        Updates one or more TCO options

        :param accuracy:
            Accuracy in seconds.
        :param validity:
            Validity in seconds.
        :param ob_delay:
            Onboard delay in seconds.
        :param default_tof:
            Default ToF in seconds. This value is used if the ToF estimator
            does not find a matching interval.
        """
        req = tco_pb2.TcoConfig()
        if accuracy is not None:
            req.accuracy = accuracy
        if validity is not None:
            req.validity = validity
        if ob_delay is not None:
            req.onboardDelay = ob_delay
        if default_tof is not None:
            req.defaultTof = default_tof

        url = f"/tco/{self._instance}/{self._service}/config"
        self.ctx.post_proto(url, data=req.SerializeToString())  # TODO should be patch

    def add_tof_interval(
        self, start: datetime.datetime, stop: datetime.datetime, polynomial: List[float]
    ):
        """
        Defines a ToF interval for the ERT range ``[start, stop]``, specifying
        a polynomial function of the form: `tof = a + bx + cx^2 + ...` where `x`
        is ERT minus the provided start date.

        :param start:
            ERT start
        :param stop:
            ERT stop
        :param polynomial:
            Coefficients in the order ``[a, b, c, ...]``
        """
        self.add_tof_intervals([TofInterval(start, stop, polynomial)])

    def add_tof_intervals(self, intervals: List[TofInterval]):
        """
        Adds multiple ToF intervals at once.

        :param intervals:
            List of ToF intervals.
        """
        req = tco_pb2.AddTimeOfFlightIntervalsRequest()
        for interval in intervals:
            tof = req.intervals.add()
            tof.ertStart.MergeFrom(to_server_time(interval.start))
            tof.ertStop.MergeFrom(to_server_time(interval.stop))
            tof.polCoef.extend(interval.polynomial)

        url = f"/tco/{self._instance}/{self._service}/tof:addIntervals"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def remove_tof_intervals(self, start: datetime.datetime, stop: datetime.datetime):
        """
        Removes previously registered ToF intervals whose start date
        falls in the specified range ``[start, stop]``.

        :param start:
            ERT start
        :param stop:
            ERT stop
        """
        req = tco_pb2.DeleteTimeOfFlightIntervalsRequest()
        req.start.MergeFrom(to_server_time(start))
        req.stop.MergeFrom(to_server_time(stop))

        url = f"/tco/{self._instance}/{self._service}/tof:deleteIntervals"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def reset_coefficients(self):
        """
        Resets current TCO coefficients, as well as any
        collected samples.
        """
        url = f"/tco/{self._instance}/{self._service}:reset"
        self.ctx.post_proto(url)

    def override_coefficients(
        self, utc: datetime.datetime, obt: int, gradient: float = 0, offset: float = 0
    ):
        """
        Manually override the assocation between UTC and
        onboard time.

        .. note::
            If later on you want to revert to automatically computed
            coefficients, use :meth:`reset_coefficients`.

        :param utc:
            UTC
        :param obt:
            Onboard time
        :param gradient:
            Gradient
        :param offset:
            Offset
        """
        req = tco_pb2.TcoCoefficients()
        req.utc.MergeFrom(to_server_time(utc))
        req.obt = obt
        req.gradient = gradient
        req.offset = offset

        url = f"/tco/{self._instance}/{self._service}/coefficients"
        self.ctx.post_proto(url, data=req.SerializeToString())
