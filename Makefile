

proto: frame_controller/frame_controller_pb2.py


frame_controller/frame_controller_pb2.py:  frame_controller/frame_controller.proto
	python -m grpc_tools.protoc -Iframe_controller/ \
 						--python_out=frame_controller/ \
 						--grpc_python_out=frame_controller/ \
						frame_controller/frame_controller.proto


.PHONY: proto
