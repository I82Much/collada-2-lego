import sys
import numpy
import Image

from ldraw.colours import *
from ldraw.pieces import Group, Piece, Vector
from ldraw.figure import *
from ldraw.geometry import *

BRICK_WIDTH = 20
BRICK_HEIGHT = 24

def enum(**enums):
  return type('Enum', (), enums)

Orientation = enum(HORIZONTAL = 0, VERTICAL = 1)
GridState = enum(EMPTY = 255, TO_FILL = 1, ALREADY_FILLED = 3)

# common lego shape sizes
pieces_map = {
  (1,4) : "3010",
  (1,3) : "3622",
  (1,2) : "3004",
  (1,1) : "3005",
  
  (2,4) : "3001",
  (2,3) : "3002",
  (2,2) : "3003",
}


def get_pieces(array):
  
  piece_map = {}
  # numpy arrays are in column major order
  width, height = array.shape
  
  # create a new 2d array of same dimensions as the image
  new_grid = numpy.zeros(array.shape, dtype=numpy.uint8)
  
  num_black = 0
  for row in range(height):
    for column in range(width):
      # if array[row][column] == False:
      if array[column][row] < 10:
        new_grid[column][row] = GridState.TO_FILL
        num_black += 1
      else:
        new_grid[column][row] = GridState.EMPTY
  
  print new_grid
        
  num_missing_pieces = 0
  # at this point, we have a 2d array with 0s in empty spots, and 1 where
  # we need a piece to fill it.  Use a simple greedy strategy where we work
  # left to right, top to bottom
  for row in range(height):
    for column in range(width):
      
      # print (row, column)
      found_piece = False
      if new_grid[column][row] == GridState.TO_FILL:

        # ordered from biggest to smallest
        available_pieces = reversed(sorted(pieces_map))
        available_orientations = [Orientation.HORIZONTAL, Orientation.VERTICAL]
        
        piece_orientation_pairs = [(piece, orientation) for piece in available_pieces for orientation in available_orientations]
        
        for piece, orientation in piece_orientation_pairs:
          if piece_fits(new_grid, piece, orientation, row, column):
            piece_map[(row,column)] = (piece, orientation)
            # mark up the grid to indicate that the spaces this piece goes in have
            # been filled.
            for (row_, column_) in get_locations(piece, orientation, row, column):
              # print "assinging ", row_, column_, " to be filled."
              new_grid[column_][row_] = GridState.ALREADY_FILLED
              found_piece = True
              
            print "Piece %s fit at row %d column %d orientation %d" %(piece, row, column, orientation)
            print "New grid: "
            print new_grid
            break
          else:
            print "piece %s didn't fit with orientation %d at row %d column %d" %(piece, orientation, row, column)
            print new_grid[column][row]
            print get_locations(piece, orientation, row, column)
        
        # end of loop          
        if not found_piece:
          print "Failed to find a piece for row %d col %d" %(row, column)
          num_missing_pieces += 1
  
  print num_missing_pieces
  
  
  # Image.fromarray(array).show()
  # Image.fromarray(new_grid).show()
  
  print "Num black squares: ", num_black
  print len(piece_map)
  
  # print piece_map
  return piece_map



# grid is a numpy array
def piece_fits(grid, piece, orientation, row, column):
  # these are all the grid squares the brick will take up
  locations = get_locations(piece, orientation, row, column)
  num_columns, num_rows = grid.shape
  
  valid_space = lambda(r, c): (0 <= r < num_rows) and (0 <= c < num_columns)
  space_must_be_filled = lambda (r, c): grid[c][r] == GridState.TO_FILL
  for _row, _column in locations:
    if not valid_space( (_row, _column) ):
      print "not a valid space."
      return False
    elif not space_must_be_filled( (_row, _column) ):
      print "expected would be filled, was ", grid[_column][_row]
      return False
  return True
  
def get_locations(piece, orientation, row, column):
  """
  Given a piece in the format (width, length), an orientation (vertical or horizontal),
  and the location of the upper left hand corner of the piece, returns all the
  (row, column) locations that the piece will take up.
  """
  # pieces are given in form width, length
  width, length = piece
  row_span = 0
  col_span = 0
  if orientation == Orientation.VERTICAL:
    row_span = length
    col_span = width
  else:
    row_span = width
    col_span = length
  
  return [ (row + y, column + x) for x in range(col_span) for y in range(row_span) ]
    
    
    
  
def get_ldraw(piece_map):
  print piece_map
  pieces = []
  # map from location to piece
  for location, (piece, orientation) in sorted(piece_map.items()):
    piece_string = pieces_map[piece]
    color = Black
    
    # we need to translate from image coordinates into ldraw coordinates
    image_x, image_y = location
    
    x_offset = image_y * BRICK_WIDTH
    y_offset = 0
    # x axis in the image matches z axis when viewed overhead in ldraw 
    z_offset = image_x * BRICK_WIDTH
    
    
    width, length = piece
    if orientation == Orientation.HORIZONTAL:
      # z in world space = x in image space
      # x in world space = y in image space
      z_offset += (width-1.0) / 2 * BRICK_WIDTH
      x_offset += (length-1.0) / 2 * BRICK_WIDTH
    else:
      z_offset += (length-1.0) / 2 * BRICK_WIDTH
      x_offset += (width-1.0) / 2 * BRICK_WIDTH
    
    
    orientation_matrix = Identity()
    if (orientation == Orientation.VERTICAL):
      orientation_matrix = orientation_matrix.rotate(90, YAxis)
    
    the_piece = Piece(color, Vector(x_offset, y_offset, z_offset), orientation_matrix, piece_string)
    pieces.append(the_piece)
    
    
  # by default, pieces are oriented left to right (horizontal) when viewed from above
  # furthermore, pieces are centered.  Need to translate to get upper left corner where it belongs
  return pieces

def main():
  args = sys.argv[1:]
  
  print args
  
  image_file = args[0]
  # convert to black and white,
  image = Image.open(image_file).resize((64,64)).convert(mode="L")
  array = numpy.array(image)
  
  # image_file = "black"
  # array = numpy.identity(16) * 255#(16,16))
  
  pieces = get_pieces(array)
  ldraw_pieces = get_ldraw(pieces)
  
  output_file = open(image_file + ".ldr", "w")
  output_file.writelines( "\n".join( repr(x) for x in ldraw_pieces) )
  output_file.close()


def test_get_locations():
  two_by_three = (2,3)
  upper_left = (0,0)
  locations = get_locations(two_by_three, Orientation.HORIZONTAL, 0, 0)
  assert len(locations) == 6
  print locations
  # assert set(locations) == set([(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)])
  
  
  locations = get_locations(two_by_three, Orientation.VERTICAL, 0, 0)
  assert len(locations) == 6
  # assert set(locations) == set([(0,0), (1,0), (2,0), (1,0), (1,1), (1,2)])
  print locations
  
  

# if __name__ == '__main__':
#   main()
# test_get_locations()
main()