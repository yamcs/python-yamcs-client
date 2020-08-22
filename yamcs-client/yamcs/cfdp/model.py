import threading

from yamcs.core.helpers import parse_server_time
from yamcs.protobuf.cfdp import cfdp_pb2


class Transfer:
    """
    Represents a CFDP transfer.
    """

    def __init__(self, proto, cfdp_client):
        self._proto = proto
        self._cfdp_client = cfdp_client

    @property
    def id(self):
        """Yamcs-local transfer identifier."""
        return self._proto.id

    @property
    def bucket(self):
        return self._proto.bucket

    @property
    def object_name(self):
        return self._proto.objectName

    @property
    def remote_path(self):
        return self._proto.remotePath

    @property
    def time(self):
        """Time when the transfer was started."""
        if self._proto.HasField("startTime"):
            return parse_server_time(self._proto.startTime)
        return None

    @property
    def reliable(self):
        """True if this is a Class 2 CFDP transfer."""
        return self._proto.reliable

    @property
    def state(self):
        """Current transfer state."""
        if self._proto.HasField("state"):
            return cfdp_pb2.TransferState.Name(self._proto.state)
        return None

    @property
    def size(self):
        """Total bytes to transfer."""
        return self._proto.totalSize

    @property
    def transferred_size(self):
        """Total bytes already transferred."""
        return self._proto.sizeTransferred

    def is_complete(self):
        """
        Returns whether this transfer is complete. A transfer
        can be completed, yet still failed.
        """
        return self.state == "FAILED" or self.state == "COMPLETED"

    def is_success(self):
        """
        Returns true if this transfer was completed successfully.
        """
        return self.state == "COMPLETED"

    @property
    def error(self):
        """Error message in case the transfer failed."""
        if self.state == "FAILED" and self._proto.HasField("failureReason"):
            return self._proto.failureReason
        return None

    def pause(self):
        """
        Pause this transfer
        """
        self._cfdp_client.pause_transfer(self.id)

    def resume(self):
        """
        Resume this transfer
        """
        self._cfdp_client.resume_transfer(self.id)

    def cancel(self):
        """
        Cancel this transfer
        """
        self._cfdp_client.cancel_transfer(self.id)

    def await_complete(self, timeout=None):
        """
        Wait for the transfer to be completed.

        :param float timeout: The amount of seconds to wait.
        """
        completed = threading.Event()

        def callback(updated_transfer):
            if updated_transfer.id == self.id:
                self._proto = updated_transfer._proto
                if self.is_complete():
                    completed.set()

        self._cfdp_client.create_transfer_subscription(on_data=callback)

        if not completed.wait(timeout=timeout):
            # Remark that a timeout does *not* mean that the underlying
            # work is canceled.
            raise TimeoutError("Timed out.")
