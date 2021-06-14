from yamcs.core.helpers import to_server_time
from yamcs.protobuf.tco import tco_pb2
from yamcs.tco.model import TCOStatus, TofInterval


class TCOClient:
    """
    Client for interacting with a Time Correlation service managed by Yamcs.
    """

    def __init__(self, ctx, instance, service):
        super(TCOClient, self).__init__()
        self.ctx = ctx
        self._instance = instance
        self._service = service

    def get_status(self):
        """
        Retrieve the TCO status.

        :rtype: .TCOStatus
        """
        response = self.ctx.get_proto(f"/tco/{self._instance}/{self._service}/status")
        message = tco_pb2.TcoStatus()
        message.ParseFromString(response.content)
        return TCOStatus(message)

    def reconfigure(
        self, accuracy=None, validity=None, ob_delay=None, default_tof=None
    ):
        """
        Updates one or more TCO options

        :param Optional[float] accuracy: Accuracy in seconds.
        :param Optional[float] validity: Validity in seconds.
        :param Optional[float] ob_delay: Onboard delay in seconds.
        :param Optional[float] default_tof: Default ToF in seconds. This value is used
                                            if the ToF estimator does not find a
                                            matching interval.
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

    def add_tof_interval(self, start, stop, polynomial):
        """
        Defines a ToF interval for the ERT range ``[start, stop]``, specifying
        a polynomial function of the form: `tof = a + bx + cx^2 + ...` where `x`
        is ERT minus the provided start date.

        :param ~datetime.datetime start: ERT start
        :param ~datetime.datetime stop: ERT stop
        :param float[] polynomial: Coefficients in the order ``[a, b, c, ...]``
        """
        self.add_tof_interval([TofInterval(start, stop, polynomial)])

    def add_tof_intervals(self, intervals):
        """
        Adds multiple ToF intervals at once.

        :param .TofInterval[] intervals: List of ToF intervals.
        """
        req = tco_pb2.AddTimeOfFlightIntervalsRequest()
        for interval in intervals:
            tof = req.intervals.add()
            tof.ertStart = to_server_time(interval.start)
            tof.ertStop = to_server_time(interval.stop)
            tof.polCoef.extend(interval.polynomial)

        url = f"/tco/{self._instance}/{self._service}/tof:addIntervals"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def remove_tof_intervals(self, start, stop):
        """
        Removes previously registered ToF intervals whose start date
        falls in the specified range ``[start, stop]``.

        :param ~datetime.datetime start: ERT start
        :param ~datetime.datetime stop: ERT stop
        """
        req = tco_pb2.DeleteTimeOfFlightIntervalsRequest()
        req.start = to_server_time(start)
        req.stop = to_server_time(stop)

        url = f"/tco/{self._instance}/{self._service}/tof:deleteIntervals"
        self.ctx.post_proto(url, data=req.SerializeToString())

    def reset_coefficients(self):
        """
        Resets current TCO coefficients, as well as any
        collected samples.
        """
        url = f"/tco/{self._instance}/{self._service}:reset"
        self.ctx.post_proto(url)

    def override_coefficients(self, utc, obt, gradient=0, offset=0):
        """
        Manually override the assocation between UTC and
        onboard time.

        .. note::
            If later on you want to revert to automatically computed
            coefficients, use :meth:`reset_coefficients`.

        :param ~datetime.datetime utc: UTC
        :param int obt: Onboard time
        :param Optional[float] gradient: Gradient
        :param Optional[float] offset: Offset
        """
        req = tco_pb2.TcoCoefficients()
        req.utc = to_server_time(utc)
        req.obt = obt
        req.gradient = gradient
        req.offset = offset

        url = f"/tco/{self._instance}/{self._service}/coefficients"
        self.ctx.post_proto(url, data=req.SerializeToString())
