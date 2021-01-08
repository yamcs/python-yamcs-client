from yamcs.core.helpers import parse_server_time


class TCOStatus:
    """
    TCO Status
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def coefficients(self):
        """
        Current coefficients. Or ``None`` if the synchronization is not
        yet established.
        """
        if self._proto.HasField("coefficients"):
            return TCOCoefficients(self._proto.coefficients)
        return None

    @property
    def coefficients_time(self):
        """
        Time when the coefficients have been computed
        """
        if self._proto.HasField("coefficientsTime"):
            return parse_server_time(self._proto.coefficientsTime)
        return None

    @property
    def deviation(self):
        """
        Last computed deviation
        """
        if self._proto.HasField("deviation"):
            return self._proto.deviation
        return None

    @property
    def samples(self):
        """
        The last accumulated samples
        """
        return [TCOSample(p) for p in self._proto.samples]


class TCOCoefficients:
    """
    TCO Coefficients
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def utc(self):
        if self._proto.HasField("utc"):
            return parse_server_time(self._proto.utc)
        return None

    @property
    def obt(self):
        if self._proto.HasField("obt"):
            return self._proto.obt
        return None

    @property
    def gradient(self):
        if self._proto.HasField("gradient"):
            return self._proto.gradient
        return None

    @property
    def offset(self):
        if self._proto.HasField("offset"):
            return self._proto.offset
        return None


class TCOSample:
    def __init__(self, proto):
        self._proto = proto

    @property
    def utc(self):
        if self._proto.HasField("utc"):
            return parse_server_time(self._proto.utc)
        return None

    @property
    def obt(self):
        if self._proto.HasField("obt"):
            return self._proto.obt
        return None

    def __str__(self):
        return f"({self.utc}, {self.obt})"


class TofInterval:
    """
    ToF interval for the ERT range ``[start, stop]``, specifying
    a polynomial function of the form: `tof = a + bx + cx^2 + ...` where `x`
    is ERT minus the provided start date.
    """

    def __init__(self, start, stop, polynomial):
        """
        :param ~datetime.datetime start: ERT start
        :param ~datetime.datetime stop: ERT stop
        :param float[] polynomial: Coefficients in the order ``[a, b, c, ...]``
        """
        self.start = start
        self.stop = stop
        self.polynomial = polynomial
