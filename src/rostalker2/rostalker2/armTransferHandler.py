import rclpy
from rclpy.node import Node
from threading import Thread, Lock
import sys
import time
from rostalker2interface.srv import *
from rostalker2interface.msg import *
import os
import os.path
from os import path
from pathlib import Path
import importlib.util
from rostalker2.retry_functions import *
from rostalker2.register_functions import *
from rostalker2.register_functions import _register, _deregister_node
from rostalker2.worker_info_api import *
from rostalker2.worker_info_api import _get_node_info, _get_node_list, get_node_info

# TODO: arm is a shared resource has to be able to lock itself
# TODO: figure out how to integrate arm code

class ArmTransferHandler(Node):
	def __init__(self, name):
		# Node creation
		super().__init__("arm_transfer_handler_" + name) # User specifies name
		self.name = name

		# Lock creation
		self.arm_lock = Lock() # Only one can access arm at a time

		# Store who is doing the transfer and store respective locks
		self.transfer_queue = []
		self.completed_queue = []

		# Readabilty
		self.state = { #TODO maybe a sync with the master
			"BUSY":1,
			"READY":0
		}
		self.status = {
			"ERROR":1,
			"SUCCESS":0,
			"WARNING":2,
			"FATAL":3
		}

		# Path setup
		path = Path()
		self.home_location = str(path.home())
		self.module_location = self.home_location + "/ros2tests/src/OT2_Modules/"

		# Create clients
		self.get_id_cli = self.create_client(GetId, '/arm/%s/get_id'%self.name)

		# Get ID and confirm name from manager
		self.get_id_name()

		# Create subscribers TODO

		# Create services
		self.transfer_service = self.create_service(Transfer, "/arm/%s/transfer"%self.id, self.transfer_handler) # Handles transfer service requests
#		self.wait_service = self.create_service(WaitForTransfer, "/arm/%s/wait_for_transfer"%self.id, self.wait_handler_old) # Handles transfer service requests

		# Initialization Complete
		self.get_logger().info("Arm Transfer handler for ID: %s name: %s initialization completed"%(self.id, self.name))

	# Gets own id and name from manager
	def get_id_name(self):
		# Create a request
		request = GetId.Request()

		# Wait for service
		while(not self.get_id_cli.wait_for_service(timeout_sec=2)):
			self.get_logger().info("Service not available, trying again...")

		# Call client
		future = self.get_id_cli.call_async(request)
		rclpy.spin_until_future_complete(self, future) #TODO: find a way to switch to the while loop
#		while(future.done() == False):
#			time.sleep(1) # 1 second timeout
		if(future.done()):
			try:
				response = future.result()
				# name check
				if(not response.name == self.name):
					raise Exception()

				self.id = response.id
				self.type = response.type
			except Exception as e:
				self.get_logger().error("Error occured: %r"%(e,))
				return self.status['ERROR']
			else:
				return self.status['SUCCESS']


	# Handles transfer service requests
	def transfer_handler(self, request, response): #TODO: error handling
		
		# Acquire lock
		self.arm_lock.acquire()
		
		# Get request
		to_name = request.to_name
		to_id = request.to_id
		from_name = request.from_name
		from_id = request.from_id
		item = request.item
		cur_node = request.cur_name
		other_node = request.other_name
		
		# Create response
		response = Transfer.Response()
		
		# Create identifier
		identifier_cur = from_name + " " + to_name + " " + item + " Node: " + cur_node
		identifier_other = from_name + " " + to_name + " " + item + " Node: " + other_node
		
		# Check to see if the transfer already completed
		completed = False
		for item in self.completed_queue:
			if(item == identifier_other): # Transfer already completed
				completed = True
				self.completed_queue.remove(item) # remove from completed queue
				break
		if(completed == True): # We are done
			response.status = response.SUCCESS
			self.arm_lock.release() # Realise lock
			return response
		
		# Check to see if other side is ready 
		both_ready = False
		for item in self.transfer_queue:
			if(item == identifier_other): # Item is waiting can continue
				both_ready = True
				self.transfer_queue.remove(item) # delete from queue
				break
				
		# Check if in queue
		in_queue = False
		for item in self.transfer_queue:
			if(item == identifier_cur):
				in_queue = True
				break # in queue already
				
		# Adds current transfer identifier for the other side to verify
		if(in_queue == False):
			self.transfer_queue.append(identifier_cur)
			
		# If both aren't ready we return WAITING
		if(both_ready == False):
			response.status = response.WAITING # Still waiting on the other side
			self.arm_lock.release() # Realise lock
			return response 
		
		# Both sides are ready complete the transfer and the transfer hasn't already been completed
		# Do the transfer
		self.get_logger().info("Attempting to transfer complete transfer %s" % identifier_cur)
		time.sleep(2) #TODO actual transfer code
		self.get_logger().info("Transfer %s is complete"%identifier_cur)
		
		# Add to completed queue
		self.completed_queue.append(identifier_cur) # For the node waiting on it
		self.transfer_queue.remove(identifier_cur) # Remove our identifier from queue
		self.arm_lock.release() # Release lock
		response.status = response.SUCCESS
		return response
				


	# Handles transfer service requests
	# TODO: DELETE *** This is old
	def transfer_handler_old(self, request, response):
		# TODO if it sees another transfer request that also points to itself (to of the request)
		# Notify the user that a deadlock is occuring

		# only one transfer at a time
		self.arm_lock.acquire()

		# Get request information
		to_name = request.to_name
		to_id = request.to_id
		from_name = request.from_name
		from_id = request.from_id
		item = request.item

		# Create response
		response = Transfer.Response()

		# Get node (to/from) information (TODO future support for locating the OT-2s)
#		to_entry = get_node_info(to_name) # Search by name for now
#		from_entry = get_node_info(from_name)

		# error / warning   TODO: move over to wait
#		if(to_entry['type'] == '-1'):
#			response.status = response.ERROR # Error
#		if(from_entry['type'] == '-1'):
#			response.status = response.ERROR # Error
#		if(response.status == response.ERROR):
#			self.arm_lock.release() # release lock
#			return response # Exit due to error

		# Set identifier and lock
		identifier = from_name + " " + to_name + " " + item
		self.cur_transfer = identifier # Identifier for this current transfer

		# Spin for the other robot waiting for it
		while(not self.cur_wait == identifier):
			self.get_logger().info("Waiting on the location to transfer to...")
			time.sleep(2) # timeout 2 seconds

		# At this point both points are ready to recieve begin transfer
		#TODO: actual arm transfer code
		self.get_logger().info("Transfering from %s to %s"%(from_name, to_name))
		time.sleep(2) # 2 second sleep for place holder
		self.get_logger().info("Transfer complete from %s to %s"%(from_name, to_name))

		# Let waiter know everything is done
		self.cur_transfer = ""
		self.cur_wait = ""

		# Release lock and return status
		response.status = response.SUCCESS
		self.arm_lock.release()
		return response

	# Handles wait services requests
	# TODO: DELETE *** this is old
	def wait_handler_old(self, request, response): #TODO this function can't be a service (has to be a topic or needs to run on separate node)
		# don't need to acquire lock since multiple things can be waiting on at once and no writes are needed

		# Get request
		to_name = request.to_name
		to_id = request.to_id
		from_name = request.from_name
		from_id = request.from_id
		item = request.item

		# Create response
		response = WaitForTransfer.Response()


		print("running")
		# Begin waiting on identifier to be published
		identifier = from_name + " " + to_name + " " + item #TODO: add support for like max wait time to avoid deadlocks
		while(not self.cur_transfer == identifier):
			time.sleep(2) # timeout 2 seconds

		# It is out turn to transfer
		self.cur_wait = identifier # Lets the transfer happen

		# Spin for transfer to finish
		while(self.cur_wait == identifier):
			time.sleep(2) # timeout 2 seconds

		# all done return status
		response.status = response.SUCCESS
		return response

def main(args=None):
	rclpy.init(args=args)

	if(len(sys.argv) != 2):
		print("need 1 arguments")
		sys.exit(1)
	name = str(sys.argv[1])

	arm_transfer_node = ArmTransferHandler(name)
	try:
		rclpy.spin(arm_transfer_node)
#		while True:
#			rclpy.spin_once(arm_transfer_node)
#			arm_transfer_node.get_logger().info("spin")
	except Exception as e:
		arm_transfer_node.get_logger().fatal("Error %r"%(e,))
	except:
		arm_transfer_node.get_logger().error("Terminating...")

	# End
	arm_transfer_node.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
	main()
