import serial


def test_robot(robot_id, comms):
	print 'Going forwards:\n'
	comms.write('%s_RUN_ENGINE 500 500\n' % robot_id)
	print 'Going backwards:\n'
	comms.write('%s_RUN_ENGINE -500 -500\n' % robot_id)
	print 'Turning left:\n'
	comms.write('%s_RUN_ENGINE -500 500\n' % robot_id)
	print 'Turning right:\n'
	comms.write('%s_RUN_ENGINE 500 -500\n' % robot_id)



if __name__ == '__main__':
	comms = Arduino('/dev/ttyUSB0', 115200, 1, 1)
	test_robot('D', comms)
	#test_robot('A', comms)