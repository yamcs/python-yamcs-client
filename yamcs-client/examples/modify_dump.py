import struct

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _VarintBytes
from yamcs.protobuf.table import table_pb2

"""
This file gives some clues as to how one might modify a raw
table dump, for example to manually apply data migrations
between a dump and restore.

This is a rare use case. The decode/encode logic is not easy
to come up with, so we keep it around for reference.
"""


def read_in_chunks(file_object, chunk_size=1024):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def read_rows(file_object):
    buf = None
    for chunk in read_in_chunks(file_object):
        if buf is None:
            buf = chunk
        else:
            buf += chunk

        while len(buf):
            try:
                # n is advanced beyond the varint
                msg_len, n = _DecodeVarint32(buf, 0)
            except IndexError:
                break  # Need another chunk

            if n + msg_len > len(buf):
                break  # Need another chunk

            msg_buf = buf[n : (n + msg_len)]
            buf = buf[(n + msg_len) :]
            message = table_pb2.Row()
            message.ParseFromString(msg_buf)
            yield message


def replace_cell_data(data, search, replacement):
    utf_like = data.decode("utf-8")
    return utf_like.replace(search, replacement).encode("utf-8")


def mutf8_decode(data):
    # Just cut off the leading short
    return str(data[2:], "utf-8")


def mutf8_encode(string_value):
    utf8 = string_value.encode("utf-8")
    length = len(utf8)
    data = struct.pack("!H", length)
    format = "!" + str(length) + "s"
    return data + struct.pack(format, utf8)


if __name__ == "__main__":

    with open("cmdhist.dump", "rb") as f:
        with open("cmdhist_modified.dump", "wb") as fout:
            columns = {}
            for row in read_rows(f):
                # Column mapping only set on first row
                for col in row.columns:
                    columns[col.id] = col.name

                for cell in row.cells:
                    if columns[cell.columnId] == "Acknowledge_C_Status":
                        if "ACK C: OK" == mutf8_decode(cell.data):
                            cell.data = mutf8_encode("OK")

                fout.write(_VarintBytes(row.ByteSize()))
                fout.write(row.SerializeToString())
