import sys
import numpy
import Image

from ldraw.colours import *
from ldraw.pieces import Group, Piece, Vector
from ldraw.figure import *


BRICK_WIDTH = 20
BRICK_HEIGHT = 24


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

HORIZONTAL = 0
VERTICAL = 1

def get_pieces(array):
  
  # step 1: get it working with just 1x1 pieces
  
  # wherever there is a *black* pixel, put a 1x1 piece
  piece = (1,1)
  piece_map = {}
  height, width = array.shape
  for row in range(height):
    for column in range(width):
      # if array[row][column] == False:
      if array[row][column] < 10:
        piece_map[(row,column)] = (piece, VERTICAL)
  return piece_map
  
def get_ldraw(piece_map):
  pieces = []
  # map from location to piece
  for location, (piece, orientation) in piece_map.items():
    piece_string = pieces_map[piece]
    
    # we need to translate from image coordinates into ldraw coordinates
    image_x, image_y = location
    
    x_offset = image_y * BRICK_WIDTH
    y_offset = 0
    # x axis in the image matches z axis when viewed overhead in ldraw 
    z_offset = -image_x * BRICK_WIDTH
    
    
    the_piece = Piece(Black, Vector(x_offset, y_offset, z_offset), Identity(), piece_string)
    pieces.append(the_piece)
  return pieces

def main():
  args = sys.argv[1:]
  
  print args
  
  image_file = args[0]
  # convert to black and white,
  image = Image.open(image_file).resize((64,64)).convert(mode="L")
  array = numpy.array(image)
  pieces = get_pieces(array)
  ldraw_pieces = get_ldraw(pieces)
  
  output_file = open(image_file + ".ldr", "w")
  output_file.writelines( "\n".join( repr(x) for x in ldraw_pieces) )
  output_file.close()

# if __name__ == '__main__':
#   main()

main()