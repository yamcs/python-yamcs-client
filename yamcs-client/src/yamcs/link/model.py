from yamcs.protobuf.cop1 import cop1_pb2


class Cop1Status:
    """
    COP1 status
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def cop1_active(self):
        return self._proto.cop1Active

    @property
    def state(self):
        if self._proto.HasField("state"):
            return cop1_pb2.Cop1State.Name(self._proto.state)
        return None

    @property
    def bypass_all(self):
        if self._proto.HasField("setBypassAll"):
            return self._proto.setBypassAll
        return None

    @property
    def v_s(self):
        if self._proto.HasField("vS"):
            return self._proto.vS
        return None

    @property
    def nn_r(self):
        if self._proto.HasField("nnR"):
            return self._proto.nnR
        return None

    def __str__(self):
        line = f"COP1_ACTIVE: {self.cop1_active}"
        if self.cop1_active:
            return line + f", state: {self.state}, nn_r: {self.nn_r}, v_s: {self.v_s}"
        else:
            return line + f", bypass_all: {self.bypass_all}"


class Cop1Config:
    """
    COP1 configuration
    """

    def __init__(self, proto):
        self._proto = proto

    @property
    def vc_id(self):
        """
        Virtual Channel ID.
        """
        return self._proto.vcId

    @property
    def window_width(self):
        return self._proto.windowWidth

    @property
    def timeout_type(self):
        return cop1_pb2.TimeoutType.Name(self._proto.timeoutType)

    @property
    def tx_limit(self):
        return self._proto.txLimit

    @property
    def t1(self):
        return self._proto.t1 / 1000.0

    def __str__(self):
        res = f"VC_ID: {self.vc_id}, win: {self.window_width}"
        res += f", timeout_type: {self.timeout_type}"
        return res + f", tx_limit: {self.tx_limit}, t1: {self.t1}"
