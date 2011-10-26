#!/opt/local/bin/python

import random
import geo
import PIL
import pymorph
import numpy
import Image
import ImageDraw
import collada
import sys
import getopt

# import Collada2LDraw
# import numpy
# import Image
# import collada
# import geo
# mesh = collada.Collada("../../models/sphere.dae")
# Collada2LDraw.save_images(Collada2LDraw.create_images(mesh), "with_multiple_edges")
# reload Collada2LDraw

# pycollada - http://collada.in4lines.com/
# http://stackoverflow.com/questions/5793642/collada-files-viewer

def calculate_bounding_box(mesh):
  min_x = min_y = min_z = 100000000
  max_x = max_y = max_z = -100000000
  
  for geom in mesh.scene.objects('geometry'):
    for prim in geom.primitives():
      for tri in prim.triangles():
        for vertex in tri.vertices:
          # unpack the vertex
          x, y, z = vertex
          min_x = min(min_x, x)
          max_x = max(max_x, x)
          min_y = min(min_y, x)
          max_y = max(max_y, x)
          min_z = min(min_z, x)
          max_z = max(max_z, x)
  return [(min_x,max_x), (min_y, max_y), (min_z, max_z)]


def get_point_of_intersection(plane, line):
  # http://en.wikipedia.org/wiki/Line-plane_intersection
  # a point on the plane
  p0 = plane.points()[0]

  # normal vector of plane
  n = normal(plane)
  
  # point on the line
  l0, l1 = line.points()
  l_vector = subtract(l1, l0)

  # p0 - l0 dot n = numerator
  numerator = geo.dot(subtract(p0, l0), n)
  denominator = geo.dot(n, l_vector)
  
  # print "numerator: %f" %numerator
  #   print "denominator: %f" %denominator
  
  # denominator is 0, numerator is nonzero --> no intersection
  if abs(denominator) < 1E-20 and numerator != 0:
    return []
  # both are zero, parallel - intersect at every point along line segment
  elif denominator == 0 and numerator == 0:
    # todo(ndunn): how to handle this case
    return []
  else:
    d = numerator / denominator

    # point of intersection = d*l + l_0
    x = l_vector[0] * d + l0.coordinates()[0]
    y = l_vector[1] * d + l0.coordinates()[1]
    z = l_vector[2] * d + l0.coordinates()[2]
    
    return geo.Point(x,y,z)


    
def scale(vector, d):
  return (vector[0] * d, vector[1] * d, vector[2] * d)    

def normal(plane):
  line = plane.normal()
  points = line.points()
  return subtract(points[1], points[0])
    
def subtract(p1, p2):
  """ subtracts two points (p1-p2) to obtain a vector between the two """
  x1,y1,z1 = p1.coordinates()
  x2,y2,z2 = p2.coordinates()
  
  dx = x1 - x2
  dy = y1 - y2
  dz = z1 - z2
  
  return (dx, dy, dz)

  

def create_image_of_intersection(mesh, bounding_box, plane):
  [(min_x,max_x), (min_y, max_y), (min_z, max_z)] = bounding_box
  width = int(max_x - min_x)
  height = int(max_y - min_y)
  
  #start it all white
  array = numpy.ones((width,height),dtype='int8')
  for i in range(width):
    for j in range(height):
      array[i][j] = 255
  
  img = Image.fromarray(array).convert("RGB")
  img_draw = ImageDraw.Draw(img)

  intersecting_triangles = find_triangles_which_intersect(mesh, plane)

  for tri in intersecting_triangles:
    # find the two points which are on opposite sides - draw a line between them
    p1, p2, p3 = [geo.Point(vertex) for vertex in tri.vertices]
    
    color = "rgb(%d,%d,%d)" %(random.randint(0, 255), random.randint(0,255), random.randint(0,255))
    
    
    # shift so that min x becomes 0.
    
    # hack: drawing between the line that's not connected.
    
    # draw line between p2, p3
    if plane.separates(p1, p2) and plane.separates(p1, p3):
      intersection1 = get_point_of_intersection(plane, geo.Line(p1,p2))
      intersection2 = get_point_of_intersection(plane, geo.Line(p1,p3))
      
      x1 = int(intersection1.coordinates()[0] - min_x)
      y1 = int(intersection1.coordinates()[1] - min_y)
      x2 = int(intersection2.coordinates()[0] - min_x)
      y2 = int(intersection2.coordinates()[1] - min_y)
      
      # get intersection point between p1, p2
      
      # x1 = int(tri.vertices[1][0] - min_x)
      #       y1 = int(tri.vertices[1][1] - min_y)
      #       x2 = int(tri.vertices[2][0] - min_x)
      #       y2 = int(tri.vertices[2][1] - min_y)
      img_draw.line([(x1, y1), (x2, y2)], width=2, fill=color)

    # draw line between p1 and p3
    elif plane.separates(p1, p2) and plane.separates(p2, p3):
      intersection1 = get_point_of_intersection(plane, geo.Line(p1,p2))
      intersection2 = get_point_of_intersection(plane, geo.Line(p2,p3))
      
      x1 = int(intersection1.coordinates()[0] - min_x)
      y1 = int(intersection1.coordinates()[1] - min_y)
      x2 = int(intersection2.coordinates()[0] - min_x)
      y2 = int(intersection2.coordinates()[1] - min_y)
      
      img_draw.line([(x1, y1), (x2, y2)], width=2, fill=color)
      # x1 = int(tri.vertices[0][0] - min_x)
      #       y1 = int(tri.vertices[0][1] - min_y)
      #       x2 = int(tri.vertices[2][0] - min_x)
      #       y2 = int(tri.vertices[2][1] - min_y)
      #       img_draw.line([(x1, y1), (x2, y2)], width=2, fill=0)
      pass
      
    # draw line between p1, p2
    elif plane.separates(p1, p3) and plane.separates(p2, p3):
      intersection1 = get_point_of_intersection(plane, geo.Line(p1,p3))
      intersection2 = get_point_of_intersection(plane, geo.Line(p2,p3))
      
      x1 = int(intersection1.coordinates()[0] - min_x)
      y1 = int(intersection1.coordinates()[1] - min_y)
      x2 = int(intersection2.coordinates()[0] - min_x)
      y2 = int(intersection2.coordinates()[1] - min_y)
      
      # x1 = int(tri.vertices[0][0] - min_x)
      #       y1 = int(tri.vertices[0][1] - min_y)
      #       x2 = int(tri.vertices[1][0] - min_x)
      #       y2 = int(tri.vertices[1][1] - min_y)
      img_draw.line([(x1, y1), (x2, y2)], width=2, fill=color)
    
    # # draw line between p1 and p2
    #     if plane.separates(p1, p2):
    #       x1 = int(tri.vertices[0][0] - min_x)
    #       y1 = int(tri.vertices[0][1] - min_y)
    #       x2 = int(tri.vertices[1][0] - min_x)
    #       y2 = int(tri.vertices[1][1] - min_y)
    #       img_draw.line([(x1, y1), (x2, y2)], width=2, fill=0)
    #     # draw line between p1 and p3  
    #     if plane.separates(p1, p3):
    #       x1 = int(tri.vertices[0][0] - min_x)
    #       y1 = int(tri.vertices[0][1] - min_y)
    #       x2 = int(tri.vertices[2][0] - min_x)
    #       y2 = int(tri.vertices[2][1] - min_y)
    #       img_draw.line([(x1, y1), (x2, y2)], width=2, fill=0)
    #     # draw line between p2 and p3
    #     if plane.separates(p2, p3):
    #       x1 = int(tri.vertices[1][0] - min_x)
    #       y1 = int(tri.vertices[1][1] - min_y)
    #       x2 = int(tri.vertices[2][0] - min_x)
    #       y2 = int(tri.vertices[2][1] - min_y)
    #       img_draw.line([(x1, y1), (x2, y2)], width=2, fill=0)
    
  return img
  

def create_images(mesh, step_size=10):
  [(min_x,max_x), (min_y, max_y), (min_z, max_z)] = calculate_bounding_box(mesh)
  arrays = []
  images = []
  # slice through the model at various z levels
  for z in range(min_z, max_z+1, step_size):# xz plane
    print z
    plane = geo.Plane(geo.Point(0,1,z), geo.Point(1,0,z), geo.Point(0,0,z))
    images.append(create_image_of_intersection(mesh, [(min_x,max_x), (min_y, max_y), (min_z, max_z)], plane))
  return images
  # this is not right, but let's just try to get something working
  # project all 3 points down 
  # for vertex in triangle.vertices:
  #         x, y, z = vertex[0], vertex[1], vertex[2]
  #       
  #         # ignore z component
  #         array[int(x + min_x)][int(y + min_y)] = 0
  
  
  # return [Image.fromarray(array).convert("RGB") for array in arrays]
  
def save_images(image_list, prefix="circle"):
  for (i, img) in enumerate(image_list):
    file_handle = open("%s_%d.png" %(prefix, i), "wb")
    img.save(file_handle)
    

#http://softsurfer.com/Archive/algorithm_0104/algorithm_0104.htm
def find_triangles_which_intersect(mesh, plane):
  intersecting_triangles = []
  
  
  # for each triangle, check whether any of the three line segments intersects the plane
  for geom in mesh.scene.objects('geometry'):
    for prim in geom.primitives():
      for tri in prim.triangles():
        p1, p2, p3 = [geo.Point(vertex) for vertex in tri.vertices]
        
        pairs = ( (p1, p2), (p1, p3), (p2, p3) )
        for pair in pairs:
          # if the plane separates the two points, then the line segment between them
          # intersects with the plane
          intersects = plane.separates(pair[0], pair[1])
          coplanar = geo.dot(pair[0].r - plane.r, plane.n) * geo.dot(pair[1].r - plane.r, plane.n) == 0
          if intersects or coplanar:
            intersecting_triangles.append(tri)
            break
  return intersecting_triangles

def parse_model(path_to_model):
  """ Attempt to load the given collada model  """
  mesh = collada.Collada(path_to_model)
  return mesh

def calculate_slice(image, width=1, fill=False):
  """
  image is a numpy binary array where element i is
  
  
  uses a greedy blobbing algorithm to assign the
  biggest pieces possible
  """
  pass

def main(argv):
  """
  
  TODO: replace getopt with argparse (http://docs.python.org/library/argparse.html#module-argparse)
  """
  try:                                
    opts, args = getopt.getopt(argv, "hm:", ["help", "model="]) 
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  
  model = None
  for opt, arg in opts:                
    if opt in ("-h", "--help"):      
      usage()
      sys.exit()
    elif opt in ("-m", "--model"): 
      model = arg
  
  if model == None:
    print "Must include the path to a .dae model"
    usage()
    sys.exit()
  else:
    parse_model(model)
  
def usage():
  print "./Collada2LDraw --model=/path/to.dae"
  print "usage"
  

if __name__ == '__main__':
  main(sys.argv[1:])