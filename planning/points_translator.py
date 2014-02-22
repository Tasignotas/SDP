class DistortionModule(object):
	def __init__(self, width, height, x_correction, y_correction):
		super(DistortionModule, self).__init__()
		self.width = width  ## !!!! These will need to come from the size we've cropped the pitch to.
		self.height = height
		self.x_correction = x_correction  # TBC
		self.y_correction = y_correction

tester = DistortionModule(640, 480, -0.016, -0.115)

def correct_coordinates(xval, yval):
 #Normalization
	norm_x = (2 * xval - tester.width) / float(tester.width)
	norm_y = (2 * yval - tester.height) / float(tester.height)

	radius = (norm_x * norm_x) + (norm_y * norm_y)

	moved_x = norm_x * (1 - tester.x_correction * radius)
	moved_y = norm_y * (1 - tester.y_correction * radius)
	
#Rounding back
	new_x = round((moved_x + 1) * tester.width / 2)
	new_y = round((moved_y + 1) * tester.height / 2)
	return(new_x, new_y)


## I realise these are daft test cases


testcoords = (137, 355)
print("The original co-ordinates were {0}".format(testcoords))
fixedtest = correct_coordinates(137, 355)
print("The undistorted co-ordinates were {0}".format(fixedtest))

testcoords = (320, 240)
print("The original co-ordinates were {0}".format(testcoords))
fixedtest = correct_coordinates(320, 240)
print("The undistorted co-ordinates were {0}, there's no distortion in the centre".format(fixedtest))

testcoords = (480, 600)
print("The original co-ordinates were {0}".format(testcoords))
fixedtest = correct_coordinates(480, 600)
print("The undistorted co-ordinates were {0}".format(fixedtest))
