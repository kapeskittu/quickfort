import re
from geometry import *

class CsvLayer:

    def __init__(self, onexit, rows=None):
        self.onexit = onexit
        self.rows = rows or []

def parse_csv_file(filename):
    layers = []

    # read file contents
    f = open(filename)
    lines = f.readlines()
    f.close()

    lines = [line.strip() for line in lines]

    # remove all quotes
    lines = [line.replace('\"', '') for line in lines]

    # break into the lines we want
    (top_line, lines) = (lines[0], lines[1:])

    # remove trailing commas from top_line
    top_line = re.sub(r',+$', '', top_line)

    # extract build type, start() command if any, and comment if any
    m = re.match(r'^#([bdpq])\w*( +start\(.+?\))?( .+)?$', top_line)
    (build_type, start_command, comment) = m.group(1, 2, 3)

    # break down start_command if given
    # expected format: start(x;y;start_comment)
    if start_command:
        m = re.match(r" +start\( *(\d+) *; *(\d+) *;? *(.+)? *\)",
            start_command)

        (start_pos, start_comment) = (Point(int(m.group(1)), int(m.group(2))),
            m.group(3))
    else:
        start_pos = None
        start_comment = None

    # clean up comment
    if comment:
        comment = comment.strip()
        comment = re.sub(r',+$', '', comment)
        comment = re.sub(r',{2,}', '', comment)
    else:
        comment = ''

    # break up csv into layers of cells, with each
    # layer separated by #> or #<

    csvlayers = []
    csv = []
    for line in lines:
        cells = line.split(',')
        c = cells[0]
        if c in ('#>', '#<'):
            newlayer = CsvLayer(['^5' if c == "#>" else '+5'], csv)
            csvlayers.append(newlayer)
            csv = []
        else:
            csv.append(cells)

    if len(csv) > 0:
        csvlayers.append(CsvLayer([], csv))

    layers = []
    for csvlayer in csvlayers:
        # fill a new Grid
        grid = Grid()
        (x, y) = (0, 0)
        for row in csvlayer.rows:
            x = 0
            for cell in row:
                cell = cell.strip()
                if (cell == '#'):
                    # end of a line
                    break
                else:
                    # Blank out marking (non-sent) chars
                    if cell in ('~', '`'): cell = ''

                    # add this csv cell to the grid
                    grid.add_cell(Point(x, y), cell)
                    x += 1 # for next column
            y += 1 # for next line
        grid.fixup()
        layers.append(GridLayer(csvlayer.onexit, grid))

    return (layers, build_type, start_pos, start_comment, comment)
