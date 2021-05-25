#!/bin/sh -e

# Ensure presence of data
sleep 20

# python alarms.py  # runs forever
python archive_breakdown.py
python archive_retrieval.py
python ccsds_completeness.py
python change_alarms.py
python change_algorithm.py
python change_calibration.py
# python command_bench.py  # runs forever
# python command_history.py  # runs forever
python commanding.py
# python cop1.py
python events.py
python links.py
python mission_time.py
# python multiple_commands.py  # runs forever
python object_storage.py
python packet_subscription.py
python parameter_subscription.py
python query_mdb.py
python read_write_parameters.py
python sql.py
