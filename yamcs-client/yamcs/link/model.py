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
        line = "COP1_ACTIVE: {}".format(self.cop1_active)
        if self.cop1_active:
            return line + ", state: {}, nn_r: {}, v_s: {}".format(
                self.state, self.nn_r, self.v_s
            )
        else:
            return line + ", bypass_all: {}".format(self.bypass_all)


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
        return "VC_ID: {}, win: {}, timeout_type: {}, tx_limit: {}, t1: {}".format(
            self.vc_id, self.window_width, self.timeout_type, self.tx_limit, self.t1
        )
