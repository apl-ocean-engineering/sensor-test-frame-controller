

proto: frame_controller/frame_controller_pb2.py


frame_controller/frame_controller_pb2.py:  frame_controller/frame_controller.proto
	python -m grpc_tools.protoc -I frame_controller/ \
	 						--python_out=frame_controller \
	 						--grpc_python_out=frame_controller \
							frame_controller/frame_controller.proto
	sed "-i" "" "-e" 's/import frame_controller_pb2/import frame_controller\.frame_controller_pb2/' frame_controller/frame_controller_pb2_grpc.py

clean:
	rm frame_controller/*pb2*.py

.PHONY: proto clean
