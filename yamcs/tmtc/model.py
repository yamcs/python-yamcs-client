from datetime import timedelta

from yamcs.core.helpers import parse_isostring, parse_value
from yamcs.types import pvalue_pb2


class ParameterData(object):

    def __init__(self, proto):
        super(ParameterData, self).__init__()
        self._proto = proto

    @property
    def parameters(self):
        return [ParameterValue(p) for p in self._proto.parameter]


class ParameterValue(object):

    def __init__(self, proto):
        super(ParameterValue, self).__init__()
        self._proto = proto

    @property
    def name(self):
        """
        An identifying name for the parameter value. Typically this is the
        fully-qualified XTCE name, but it may also be an alias depending
        on how the parameter update was requested.

        :rtype: str
        """
        if self._proto.id.namespace:
            return self._proto.id.namespace + '/' + self._proto.id.name
        return self._proto.id.name

    @property
    def generation_time(self):
        """
        Returns the time when the parameter was generated. If the parameter
        was extracted from a packet, this usually returns the packet time.

        :rtype: :class:`~datetime.datetime`
        """
        if self._proto.HasField('generationTimeUTC'):
            return parse_isostring(self._proto.generationTimeUTC)
        return None

    @property
    def reception_time(self):
        """
        Returns the time when the parameter value was received by Yamcs.

        :rtype: :class:`~datetime.datetime`
        """
        if self._proto.HasField('acquisitionTimeUTC'):
            return parse_isostring(self._proto.acquisitionTimeUTC)
        return None

    @property
    def validity_duration(self):
        """
        Returns how long this parameter value is valid.

        .. note: There is also an option when subscribing to get updated when the parameter values expire

        :rtype: :class:`~datetime.timedelta`
        """
        if self._proto.HasField('expireMillis'):
            return timedelta(milliseconds=self._proto.expireMillis)
        return None

    @property
    def raw_value(self):
        """
        Returns the raw (uncalibrated) value.

        :rtype: any
        """
        if self._proto.HasField('rawValue'):
            return parse_value(self._proto.rawValue)
        return None

    @property
    def eng_value(self):
        """
        Returns the engineering (calibrated) value.

        :rtype: any
        """
        if self._proto.HasField('engValue'):
            return parse_value(self._proto.engValue)
        return None

    @property
    def monitoring_result(self):
        if self._proto.HasField('monitoringResult'):
            return pvalue_pb2.MonitoringResult.Name(self._proto.monitoringResult)
        return None

    @property
    def range_condition(self):
        if self._proto.HasField('rangeCondition'):
            return pvalue_pb2.RangeCondition.Name(self._proto.rangeCondition)
        return None

    @property
    def validity_status(self):
        if self._proto.HasField('acquisitionStatus'):
            return pvalue_pb2.AcquisitionStatus.Name(self._proto.acquisitionStatus)
        return None

    @property
    def processing_status(self):
        return self._proto.processingStatus

    def __str__(self):
        line = '{} {} {}'.format(self.generation_time, self.name, self.eng_value)
        if self.monitoring_result:
            line += ' [' + self.monitoring_result + ']'
        return line
