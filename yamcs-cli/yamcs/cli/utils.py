from __future__ import print_function


def print_table(rows):
    widths = map(len, rows[0])
    for row in rows:
        for idx, col in enumerate(row):
            widths[idx] = max(len(str(col)), widths[idx])

    for row in rows:
        print('  '.join([
            str.ljust(str(col), width)
            for col, width in zip(row, widths)]))
