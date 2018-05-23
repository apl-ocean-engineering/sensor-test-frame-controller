

proto: frame_controller/frame_controller_pb2.py  yostlabs/imu_data_pb2.py

frame_controller/frame_controller_pb2.py:  proto/frame_controller.proto
	python -m grpc_tools.protoc -I proto/ \
	 						--python_out=frame_controller/ \
	 						--grpc_python_out=frame_controller/ \
							proto/frame_controller.proto
#	sed "-i" "" "-e" 's/import frame_controller_pb2/import frame_controller\.frame_controller_pb2/' frame_controller/frame_controller_pb2_grpc.py

yostlabs/imu_data_pb2.py:  proto/imu_data.proto
	python -m grpc_tools.protoc -I proto/ \
	 						--python_out=yostlabs/ \
	 						--grpc_python_out=yostlabs/ \
							proto/imu_data.proto

clean:
	rm frame_controller/*pb2.py
	rm -f yostlabs/*pb2.py

.PHONY: proto clean
